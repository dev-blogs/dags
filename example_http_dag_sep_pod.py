from airflow import DAG
from datetime import datetime
from kubernetes.client import V1ResourceRequirements
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

NAMESPACE = 'image-uploader'

with DAG(
    dag_id='example_http_dag_sep_pod',
    default_args=default_args,
    description='An example DAG to call an HTTP endpoint in separate pod',
    schedule_interval=None,  			 # Set to None for manual triggering
    start_date=datetime(2024, 1, 1),  		 # Adjust to your preferred start date
    catchup=False,
    tags=['example', 'http']
) as dag:
    
    task = KubernetesPodOperator(
        task_id='run_curl_in_pod',
        name='curl-task-pod',                    # Name of the pod
        namespace=NAMESPACE,                     # OpenShift namespace
        image='ubuntu:16.04',                    # Ubuntu 16.04 container image
        cmds=["/bin/bash", "-c"],                # Command shell
        arguments=[
            'apt-get update && apt-get install -y curl && '
            'curl -X GET "http://test-app-image-uploader.apps.192.168.1.21.nip.io/test" '
            '-H "Content-Type: application/json"'
        ],
        labels={"app": "airflow-task"},
        env_vars={"MY_ENV_VAR": "value"},        # Environment variables (optional)
        in_cluster=True,                         # Running within Kubernetes cluster
        is_delete_operator_pod=True,             # Deletes pod after task completion
        get_logs=True,                           # Fetches pod logs in Airflow UI
        container_resources=V1ResourceRequirements(
            requests={"cpu": "500m", "memory": "256Mi"},
            limits={"cpu": "1", "memory": "512Mi"}
        ),
    )
