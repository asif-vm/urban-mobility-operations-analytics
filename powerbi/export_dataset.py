"""Export the tested analytics mart as a Power BI-ready CSV."""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "mobility.duckdb"
OUTPUT = Path(__file__).parent / "route_daily_performance.csv"


def export() -> Path:
    if not DATABASE.exists():
        raise FileNotFoundError("Run python -m src.local_pipeline first")
    with duckdb.connect(str(DATABASE), read_only=True) as con:
        con.execute(
            "COPY (SELECT * FROM route_daily_performance ORDER BY service_date, route_name) "
            f"TO '{OUTPUT.as_posix()}' (HEADER, DELIMITER ',')"
        )
    return OUTPUT


if __name__ == "__main__":
    print(export())
