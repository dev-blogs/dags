from airflow import DAG
from datetime import datetime
from kubernetes.client import V1ResourceRequirements
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

NAMESPACE = 'image-uploader'

params = {
    "src": {
        "path": "/usr/src/data"
    }
}

with DAG(
    params=params,
    dag_id='example_app_luncher_dag_ver_2.0',
    default_args=default_args,
    description='An example DAG which runs app in separate pod',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'app']
) as dag:

    task_in_k8s_pod = KubernetesPodOperator(
        task_id='run_app_in_pod',
        name='app-launcher-task-pod',
        namespace=NAMESPACE,
        image='devblogs1/standalone-app:1.0',
        labels={"app": "airflow-task"},
        env_vars=[
            k8s.V1EnvVar(name="SPRING_APPLICATION_JSON", value='{{ dag_run.conf | tojson }}')
        ],
        volumes=[
            k8s.V1Volume(name="storage-volume", persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="storage-pvc"))
        ],
        volume_mounts=[
            k8s.V1VolumeMount(name="storage-volume", mount_path="/usr/src/data", sub_path=None)
        ],
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
        container_resources=k8s.V1ResourceRequirements(
            requests={"cpu": "250m", "memory": "256Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        ),
    )
