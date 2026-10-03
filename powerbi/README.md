# Power BI deliverable

`UrbanMobility.pbip` is the version-controlled Power BI Project entry point and
`measures.dax` contains the documented business measures. Connect Power BI
Desktop to `data/mobility.duckdb` through the DuckDB ODBC driver, or export the
`fct_route_daily` dbt model to Parquet/CSV for import. The intended report pages
are Executive Operations, Route Reliability, Capacity Utilization, and Weather
Impact. This source-controlled structure keeps the semantic measures reviewable
even when the binary Desktop file is not available in CI.

