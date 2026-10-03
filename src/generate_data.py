from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROUTES = ["Airport Express", "Tech Corridor", "University Loop", "Central Line", "Outer Ring"]
WEATHER = ["clear", "rain", "heavy_rain"]


def generate_trips(path: Path, rows: int = 25_000, seed: int = 42) -> Path:
    """Generate deterministic, privacy-safe transit operations data."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2025-01-01", tz="UTC")
    timestamps = start + pd.to_timedelta(rng.integers(0, 90 * 24 * 60, rows), unit="m")
    route = rng.choice(ROUTES, rows)
    weather = rng.choice(WEATHER, rows, p=[0.76, 0.19, 0.05])
    peak = pd.Series(timestamps).dt.hour.isin([7, 8, 9, 16, 17, 18, 19]).to_numpy()
    scheduled = rng.integers(18, 75, rows)
    traffic_delay = rng.gamma(2.0, 2.0, rows)
    weather_delay = np.select([weather == "rain", weather == "heavy_rain"], [4.0, 11.0], default=0.0)
    actual = scheduled + traffic_delay + weather_delay + peak * rng.uniform(1, 6, rows)
    capacity = rng.choice([42, 55, 70], rows, p=[0.25, 0.55, 0.20])
    boardings = np.minimum(capacity, rng.poisson(np.where(peak, capacity * 0.82, capacity * 0.48)))
    cancelled = rng.random(rows) < np.where(weather == "heavy_rain", 0.055, 0.008)
    df = pd.DataFrame(
        {
            "trip_id": [f"TRIP-{i:08d}" for i in range(1, rows + 1)],
            "event_ts": timestamps,
            "service_date": pd.Series(timestamps).dt.date,
            "route_name": route,
            "vehicle_id": [f"BUS-{n:04d}" for n in rng.integers(1, 401, rows)],
            "scheduled_minutes": scheduled,
            "actual_minutes": np.round(actual, 1),
            "delay_minutes": np.round(actual - scheduled, 1),
            "passengers": boardings,
            "capacity": capacity,
            "weather": weather,
            "cancelled": cancelled,
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=25_000)
    parser.add_argument("--output", type=Path, default=Path("data/raw/trips.csv"))
    args = parser.parse_args()
    print(generate_trips(args.output, args.rows))

