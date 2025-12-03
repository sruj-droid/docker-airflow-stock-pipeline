# dags/fetch_stock_data_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import logging

log = logging.getLogger(__name__)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="fetch_stock_data",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 * * * *",  # hourly
    catchup=False,
    max_active_runs=1,
    tags=["stocks"]
) as dag:

    def run_script(**kwargs):
        cmd = ["python", "/opt/airflow/scripts/fetch_and_store.py"]
        log.info("Running: %s", cmd)
        result = subprocess.run(cmd, capture_output=True, text=True)
        log.info("stdout:\n%s", result.stdout)
        if result.returncode != 0:
            log.error("stderr:\n%s", result.stderr)
            raise RuntimeError(f"Script failed with code {result.returncode}")

    fetch_task = PythonOperator(
        task_id="fetch_and_store_stock_data",
        python_callable=run_script,
        provide_context=True,
    )

    fetch_task

