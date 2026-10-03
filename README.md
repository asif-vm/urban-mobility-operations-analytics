# Urban Mobility Operations Analytics

An entry-level-friendly analytics engineering portfolio project that turns
privacy-safe transit events into tested operational marts and Power BI-ready
metrics. It complements, rather than duplicates, the existing retail CDC
lakehouse by focusing on Spark transformation, Airflow orchestration, dbt
testing, and business intelligence.

## What it demonstrates

- Deterministic synthetic transit data with explicit contracts
- PySpark transformations and partitioned Parquet outputs
- Airflow DAG orchestration with retries and a daily schedule
- dbt staging/mart models plus not-null and uniqueness tests
- DuckDB local warehouse for zero-cost reproducibility
- Power BI-ready analytics export, documented DAX measures, and report blueprint
- pytest, Docker, and GitHub Actions CI

## Architecture

```text
Transit events -> PySpark silver/gold -> DuckDB warehouse -> dbt marts -> Power BI
                         ^                    ^
                         +------- Airflow ----+
```

## KPIs

On-time performance, average delay, cancellations, passengers, occupancy, and
weather impact by route and service date.

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate
pip install pandas numpy duckdb pytest
python -m src.generate_data --rows 25000
python -m src.local_pipeline
python powerbi/export_dataset.py
pytest -q
```

Import `powerbi/route_daily_performance.csv` into Power BI Desktop and follow
the report layout in `powerbi/README.md`.

For the full stack, install Java 17 and `requirements.txt`, run `python -m
src.spark_pipeline`, then run `dbt build --project-dir dbt --profiles-dir dbt`.
Airflow users can install `requirements-airflow.txt` and copy or link `dags/`
into their configured Airflow home.

## Evidence boundaries

The included data is synthetic and makes no claim about a real transit agency.
The Power BI folder is source-controlled and documents the semantic layer; CI
does not render the report because Power BI Desktop is Windows-only.

## Repository map

- `src/`: generator, local warehouse pipeline, and Spark pipeline
- `dags/`: Airflow orchestration
- `dbt/`: transformation models and tests
- `powerbi/`: import-ready dataset, DAX measures, and report build guide
- `tests/`: quality and reproducibility tests
