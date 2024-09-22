from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import json
import tempfile
import os

from get_route import get_route_keys
from get_bus import fetch_and_process_bus_data
from upload import upload_to_cosmos

# Airflow DAG setup for collecting bus data every minute
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 24, 0, 0),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bus_data_pipeline',
    default_args=default_args,
    description='A DAG to fetch and process bus data',
    schedule_interval=timedelta(minutes=1),
    catchup=False,
)

def task_get_route_keys(**context):
    payload, route_dict = get_route_keys()
    # Save data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
        json.dump({'payload': payload, 'route_dict': route_dict}, temp_file)
        temp_file_path = temp_file.name
    # Push the file path to XComs
    context['ti'].xcom_push(key='route_data_file', value=temp_file_path)

def task_fetch_and_process_bus_data(**context):
    scheduled_task_time = context['execution_date']
    
    # Get file path from XComs
    temp_file_path = context['ti'].xcom_pull(key='route_data_file', task_ids='get_route_keys_task')
    # Load data from file
    with open(temp_file_path, 'r') as temp_file:
        data = json.load(temp_file)
    route_data = data['payload']
    route_dict = data['route_dict']
    
    extracted_stop_data, extracted_vehicle_data = fetch_and_process_bus_data(route_data, route_dict)
    
    for vehicle in extracted_vehicle_data:
        vehicle['Scheduled Task Time'] = scheduled_task_time.isoformat()
    
    # Save extracted data to temporary files
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as stop_file:
        json.dump(extracted_stop_data, stop_file)
        stop_file_path = stop_file.name
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as vehicle_file:
        json.dump(extracted_vehicle_data, vehicle_file)
        vehicle_file_path = vehicle_file.name
    
    # Push file paths to XComs
    context['ti'].xcom_push(key='stop_data_file', value=stop_file_path)
    context['ti'].xcom_push(key='vehicle_data_file', value=vehicle_file_path)
    
    # Clean up the route data file after use
    os.remove(temp_file_path)

def task_upload_to_cosmos(**context):
    # Pull file paths from XComs
    stop_file_path = context['ti'].xcom_pull(key='stop_data_file', task_ids='fetch_and_process_bus_data_task')
    vehicle_file_path = context['ti'].xcom_pull(key='vehicle_data_file', task_ids='fetch_and_process_bus_data_task')

    # Load data from temporary files
    with open(stop_file_path, 'r') as stop_file:
        extracted_stop_data = json.load(stop_file)
    with open(vehicle_file_path, 'r') as vehicle_file:
        extracted_vehicle_data = json.load(vehicle_file)

    # Call your upload function
    upload_to_cosmos(extracted_stop_data, extracted_vehicle_data)

    # Clean up temporary files
    os.remove(stop_file_path)
    os.remove(vehicle_file_path)

get_route_keys_task = PythonOperator(
    task_id='get_route_keys_task',
    python_callable=task_get_route_keys,
    dag=dag,
)

fetch_and_process_bus_data_task = PythonOperator(
    task_id='fetch_and_process_bus_data_task',
    python_callable=task_fetch_and_process_bus_data,
    dag=dag,
)

upload_to_cosmos_task = PythonOperator(
    task_id='upload_to_cosmos_task',
    python_callable=task_upload_to_cosmos,
    dag=dag,
)

get_route_keys_task >> fetch_and_process_bus_data_task >> upload_to_cosmos_task
