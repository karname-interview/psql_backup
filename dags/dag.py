from airflow import DAG
from datetime import datetime, timedelta

from airflow import models
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator

from kubernetes.client import models as k8s
from airflow.utils.dates import days_ago


class KOP(KubernetesPodOperator):
    template_ext = ()


# postgresql to create a backup from:
pg_domain = "ki-prd-dummy-rsc-postgresql.ki-prd-dummy"
pg_port = 5432
pg_database = "alan_touring"
pg_user = "alan"
pg_backup_prefix = "alan_touring_prd"
pg_backup_bucket = "dummy"

# configmap holding nesseccary environment variable for these task to run
# it is mounted as environment on all tasks
configmap = "dummy-prd-postgres-backup"

default_args = {
    "owner": "ArshiA Akhavan",
    "depends_on_past": False,
    "start_date": "2022-05-15",
    "email": ["letmemmakenewone@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "dummy_postgres_backup_<CICD_HASH_PLACEHOLDER>",  # do not change!
    default_args=default_args,
    schedule_interval="0 23 * * 4",
    max_active_runs=1,
    concurrency=10,
    catchup=False,
)


# dummy start task
start = DummyOperator(task_id="start", dag=dag)


# backup task
backup_command = f"./backup.sh {pg_domain} {pg_port} {pg_user} {pg_database} {pg_backup_prefix} {pg_backup_bucket}"
backup = KOP(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=["/bin/bash", "-c"],
    arguments=[f"{backup_command} > /airflow/xcom/return.json"],
    labels={"service": "dummy"},
    name="postgres_backup",
    task_id="postgres_backup",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    is_delete_operator_pod=True,
    do_xcom_push=True,
    configmaps=[configmap],
)


# check if backup is healty
restore_cmd = "check_restore dummy".split()
check_restore = KubernetesPodOperator(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=restore_cmd[0:1],
    arguments=restore_cmd[1:],
    labels={"service": "dummy"},
    name="postgres_check_restore",
    task_id="postgres_check_restore",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    is_delete_operator_pod=True,
    configmaps=[configmap],
    env_vars={
        "BACKUP_NAME": '{{ task_instance.xcom_pull(task_ids="postgres_backup", key="return_value")["name"] }}',
    },
)


# enable manual backup restore via Airflow UI
manual = BashOperator(
    task_id="manual",
    # exit_code=99 means skipable for Airflow
    bash_command="exit 99;",
    retries=0,
    dag=dag,
)


# to restore the backup generated in the task first task manualy
restore_cmd = f"restore {pg_domain} {pg_port} {pg_user} {pg_backup_prefix}".split()
restore = KubernetesPodOperator(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=restore_cmd[0:1],
    arguments=restore_cmd[1:],
    labels={"service": "dummy"},
    name="postgres_restore",
    task_id="postgres_restore",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    is_delete_operator_pod=True,
    configmaps=[configmap],
    env_vars={
        "BACKUP_NAME": '{{ task_instance.xcom_pull(task_ids="postgres_backup", key="return_value")["name"] }}',
    },
)


start >> backup >> check_restore >> manual >> restore
