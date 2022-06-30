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


start = DummyOperator(task_id="start", dag=dag)

base_command = "./backup.sh ki-dev-dummy-rsc-postgresql.ki-dev-dummy 5432 alan alan_touring alan_touring_dev dummy"
backup_cmd = f'/bin/bash -c "{base_command} > /airflow/xcom/return.json"'.split()
backup = KOP(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=["/bin/bash", "-c"],
    arguments=[f"{base_command} > /airflow/xcom/return.json"],
    labels={"service": "dummy"},
    name="postgres_backup",
    task_id="postgres_backup",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    # is_delete_operator_pod=True,
    do_xcom_push=True,
    env_vars={
        "PGPASSWORD": "touring",
        "S3_DOMAIN": "http://minio.air:9000",
        "S3_ACCESS_KEY": "minioadmin",
        "S3_SECRET_KEY": "minioadmin",
    },
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
    # is_delete_operator_pod=True,
    env_vars={
        "POSTGRESQL_USERNAME": "postgres",
        "POSTGRESQL_PASSWORD": "password",
        "PGPASSWORD": "password",
        "BACKUP_NAME": '{{ task_instance.xcom_pull(task_ids="postgres_backup", key="return_value")["name"] }}',
        "S3_DOMAIN": "http://minio.air:9000",
        "S3_ACCESS_KEY": "minioadmin",
        "S3_SECRET_KEY": "minioadmin",
    },
)

manual = BashOperator(
    task_id="manual",
    bash_command="/bin/false",
    retries=0,
    dag=dag,
)
restore_cmd = "restore ki-dev-dummy-rsc-postgresql.ki-dev-dummy 5432 alan dummy".split()
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
    # is_delete_operator_pod=True,
    env_vars={
        "BACKUP_NAME": '{{ task_instance.xcom_pull(task_ids="postgres_backup", key="return_value")["name"] }}',
        "PGPASSWORD": "touring",
        "S3_DOMAIN": "http://minio.air:9000",
        "S3_ACCESS_KEY": "minioadmin",
        "S3_SECRET_KEY": "minioadmin",
    },
)


start >> backup >> check_restore >> manual >> restore
