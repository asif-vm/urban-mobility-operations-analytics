from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="urban_mobility_daily",
    start_date=datetime(2025, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    default_args={"retries": 2},
    tags=["mobility", "spark", "dbt"],
) as dag:
    generate = BashOperator(
        task_id="generate_source_data",
        bash_command="python -m src.generate_data --rows 25000",
    )
    transform = BashOperator(
        task_id="spark_transform",
        bash_command="python -m src.spark_pipeline",
    )
    load_local_warehouse = BashOperator(
        task_id="load_local_warehouse",
        bash_command="python -m src.local_pipeline",
    )
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="dbt build --project-dir dbt --profiles-dir dbt",
    )
    generate >> transform >> load_local_warehouse >> dbt_build

