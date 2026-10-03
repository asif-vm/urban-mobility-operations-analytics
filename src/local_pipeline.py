from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pandas as pd


REQUIRED = {
    "trip_id", "event_ts", "service_date", "route_name", "vehicle_id",
    "scheduled_minutes", "actual_minutes", "delay_minutes", "passengers",
    "capacity", "weather", "cancelled",
}


def validate(df: pd.DataFrame) -> dict[str, int]:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    duplicate_ids = int(df["trip_id"].duplicated().sum())
    invalid_capacity = int((df["passengers"] > df["capacity"]).sum())
    critical_nulls = int(df[["trip_id", "event_ts", "route_name"]].isna().sum().sum())
    if duplicate_ids or invalid_capacity or critical_nulls:
        raise ValueError(
            f"Quality failure: duplicates={duplicate_ids}, invalid_capacity={invalid_capacity}, "
            f"critical_nulls={critical_nulls}"
        )
    return {"rows": len(df), "duplicate_ids": duplicate_ids, "invalid_capacity": invalid_capacity}


def build_warehouse(csv_path: Path, db_path: Path) -> dict[str, int]:
    df = pd.read_csv(csv_path)
    quality = validate(df)
    df["event_ts"] = pd.to_datetime(df["event_ts"], utc=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as con:
        con.register("incoming_trips", df)
        con.execute("CREATE OR REPLACE TABLE raw_trips AS SELECT * FROM incoming_trips")
        con.execute("""
            CREATE OR REPLACE TABLE clean_trips AS
            SELECT *,
                passengers::DOUBLE / NULLIF(capacity, 0) AS occupancy_rate,
                CASE WHEN delay_minutes <= 5 AND NOT cancelled THEN 1 ELSE 0 END AS on_time_flag
            FROM raw_trips
        """)
        con.execute("""
            CREATE OR REPLACE TABLE route_daily_performance AS
            SELECT service_date::DATE AS service_date, route_name,
                count(*) AS scheduled_trips,
                sum(cancelled::INT) AS cancelled_trips,
                round(avg(delay_minutes), 2) AS average_delay_minutes,
                round(100 * avg(on_time_flag), 2) AS on_time_pct,
                sum(passengers) AS passengers,
                round(100 * avg(occupancy_rate), 2) AS average_occupancy_pct
            FROM clean_trips GROUP BY 1, 2 ORDER BY 1, 2
        """)
        mart_rows = con.execute("SELECT count(*) FROM route_daily_performance").fetchone()[0]
    quality["mart_rows"] = int(mart_rows)
    return quality


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/trips.csv"))
    parser.add_argument("--database", type=Path, default=Path("data/mobility.duckdb"))
    args = parser.parse_args()
    print(build_warehouse(args.input, args.database))

