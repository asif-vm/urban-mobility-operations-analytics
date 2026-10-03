from pathlib import Path

import duckdb
import pandas as pd
import pytest

from src.generate_data import generate_trips
from src.local_pipeline import build_warehouse, validate


def test_pipeline_builds_quality_checked_mart(tmp_path: Path) -> None:
    source = generate_trips(tmp_path / "trips.csv", rows=1_000)
    database = tmp_path / "mobility.duckdb"
    result = build_warehouse(source, database)
    assert result["rows"] == 1_000
    assert result["duplicate_ids"] == 0
    assert result["mart_rows"] > 0
    with duckdb.connect(str(database), read_only=True) as con:
        assert con.execute("select min(on_time_pct), max(on_time_pct) from route_daily_performance").fetchone()[0] >= 0


def test_contract_rejects_duplicate_trip_ids(tmp_path: Path) -> None:
    source = generate_trips(tmp_path / "trips.csv", rows=20)
    frame = pd.read_csv(source)
    frame.loc[1, "trip_id"] = frame.loc[0, "trip_id"]
    with pytest.raises(ValueError, match="duplicates=1"):
        validate(frame)

