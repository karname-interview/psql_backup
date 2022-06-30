from airflow import DAG
from datetime import datetime, timedelta

from airflow import models
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.dummy import DummyOperator

from kubernetes.client import models as k8s
from airflow.utils.dates import days_ago


class KOP(KubernetesPodOperator):
    template_ext = ()

default_args = {
    'owner': 'ArshiA Akhavan',
    'depends_on_past': False,
    'start_date': '2022-05-15',
    'email': ['letmemmakenewone@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'dummy_postgres_backup_<CICD_HASH_PLACEHOLDER>',  # do not change!
    default_args=default_args,
    schedule_interval='0 23 * * 4',
    max_active_runs=1,
    concurrency=10,
    catchup=False,
)


start = DummyOperator(task_id='start', dag=dag)

backup_cmd = "/bin/bash -c './backup.sh ki-dev-dummy-rsc-postgresql.ki-dev-dummy 5432 alan alan_touring alan_touring_dev dummy_backups > /airflow/xcom/return.json'".split()
backup = KOP(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=backup_cmd[0:1],
    arguments=backup_cmd[1:],
    labels={"service": "dummy"},
    name="postgres_backup",
    task_id="postgres_backup",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    is_delete_operator_pod=True,
    do_xcom_push=True,
)
env_vars={
            'VAR1_FROM_XCOM': '{{ task_instance.xcom_pull(task_ids="task_xcom_set", key="xcom_key_name") }}',
        },

restore_cmd = f"echo filename is: $FILENAME".split()
check_restore = KOP(
    namespace="air",
    image="<CICD_IMAGE_PLACEHOLDER>",  # do not change!
    cmds=backup_cmd[0:1],
    arguments=backup_cmd[1:],
    labels={"service": "dummy"},
    name="postgres_backup",
    task_id="postgres_backup",
    dag=dag,
    get_logs=True,
    in_cluster=True,
    is_delete_operator_pod=True,
    env_vars={
                'FILENAME': '{{ task_instance.xcom_pull(task_ids="postgres_backup", key="resturn_value") }}',
            },
)


start >> backup >> check_restore
