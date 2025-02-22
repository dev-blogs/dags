from airflow import DAG
from datetime import datetime
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

with DAG(
    dag_id='example_http_dag',
    default_args=default_args,
    description='An example DAG to call an HTTP endpoint',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'http']
) as dag:

    # Define the task to call the HTTP endpoint
    api_call_task_1 = BashOperator(
        task_id='call_rest_api_1',
        bash_command='curl -X GET "http://test-app-image-uploader.apps.192.168.1.21.nip.io/test" -H "Content-Type: application/json"',
    )

    api_call_task_2 = BashOperator(
        task_id='call_rest_api_2',
        bash_command='curl -X GET "http://test-app-image-uploader.apps.192.168.1.21.nip.io/test" -H "Content-Type: application/json"',
    )

    api_call_task_3 = BashOperator(
        task_id='call_rest_api_3',
        bash_command='curl -X GET "http://test-app-image-uploader.apps.192.168.1.21.nip.io/test" -H "Content-Type: application/json"',
    )

    # Add additional tasks or dependencies here if needed
    [api_call_task_1, api_call_task_2, api_call_task_3]
