from airflow import DAG
from datetime import datetime
from kubernetes.client import V1ResourceRequirements
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

NAMESPACE = 'image-uploader'

with DAG(
    dag_id='example_app_luncher_dag',
    default_args=default_args,
    description='An example DAG which runs app in separate pod',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'http']
) as dag:
    
    task_in_k8s_pod = KubernetesPodOperator(
        task_id='run_app_in_pod',
        name='app-launcher-task-pod',
        namespace=NAMESPACE,
        image='devblogs1/standalone-test-app:1.0',
        labels={"app": "airflow-task"},
        env_vars={"SPRING_APPLICATION_JSON": '{"src": {"path": "/usr/bin/app"}}'},
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
        container_resources=V1ResourceRequirements(
            requests={"cpu": "250m", "memory": "256Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        ),
    )

    task_in_k8s_pod
