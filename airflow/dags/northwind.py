from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import os
from datetime import timedelta
from docker.types import Mount
import pendulum 

MELTANO_DOCKER_IMAGE = "meltano:latest"
DOCKER_NETWORK_NAME = "indicium_pipeline_airflow_meltano_network" 

HOST_PROJECT_ROOT = "/home/roboberto1403/indicium_pipeline" 
HOST_MELTANO_PATH = os.path.join(HOST_PROJECT_ROOT, "meltano")
HOST_MELTANO_CONFIG_PATH = os.path.join(HOST_MELTANO_PATH, "config")
HOST_DATA_PATH = os.path.join(HOST_PROJECT_ROOT, "data")

CONTAINER_MELTANO_PATH = "/opt/meltano"
CONTAINER_SCRIPTS_PATH = "/opt/meltano/scripts" 
CONTAINER_OUTPUT_DATA_PATH = "/opt/output_data" 
CONTAINET_CSV_CONFIG_PATH = "/opt/meltano/config"

COMMON_MELTANO_MOUNTS = [
    Mount(target=CONTAINER_MELTANO_PATH, source=HOST_MELTANO_PATH, type='bind'),
    Mount(target="/var/run/docker.sock", source="/var/run/docker.sock", type='bind'),
    Mount(target=CONTAINER_OUTPUT_DATA_PATH, source=HOST_DATA_PATH, type='bind'),
    Mount(target=CONTAINET_CSV_CONFIG_PATH, source=HOST_MELTANO_CONFIG_PATH, type='bind'),
]

with DAG(
    dag_id="northwind",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule_interval=None,
    catchup=False,
    tags=["meltano", "dbt"],
    default_args={
        "owner": "***",
        "email": ["lrbf@cin.ufpe.br"],
        "email_on_failure": True,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:
    # Tarefa 1: Extrair dados do Postgres para CSV (usando seu target-csv-postgres)
    extract_postgres = DockerOperator(
        task_id='extração_postgres',
        image=MELTANO_DOCKER_IMAGE,
        command="meltano el tap-postgres target-csv-postgres --catalog catalog_discovery.json",
        docker_url="unix://var/run/docker.sock",
        network_mode=DOCKER_NETWORK_NAME,
        auto_remove=True,
        mounts=COMMON_MELTANO_MOUNTS,
        mount_tmp_dir=False,
        working_dir=CONTAINER_MELTANO_PATH,
        environment={
            'TAP_POSTGRES_HOST': 'db_source',
            'TAP_POSTGRES_PORT': '5432',
            'TAP_POSTGRES_USER': '{{ var.value.tap_postgres_user_origem }}',
            'TAP_POSTGRES_PASSWORD': '{{ var.value.tap_postgres_password_origem }}',
            'TAP_POSTGRES_DATABASE': '{{ var.value.tap_postgres_db_origem }}',
        }
    )

    # Tarefa 2: Extrair dados do CSV de origem para CSV (usando seu target-csv-csv customizado)
    extract_csv = DockerOperator(
        task_id="extração_csv",
        image=MELTANO_DOCKER_IMAGE,
        command="meltano el tap-csv target-csv-csv",
        docker_url="unix://var/run/docker.sock",
        network_mode=DOCKER_NETWORK_NAME,
        auto_remove=True,
        mounts=COMMON_MELTANO_MOUNTS,
        mount_tmp_dir=False,
        working_dir=CONTAINER_MELTANO_PATH,
    )

    # Tarefa 3: DockerOperator para gerar a configuração JSON do tap-csv-latest dinamicamente
    generate_csv_config = DockerOperator(
        task_id='gerar_config_csv_dinamica',
        image=MELTANO_DOCKER_IMAGE,
        command=f"python {CONTAINER_SCRIPTS_PATH}/generate_csv_config.py",
        docker_url="unix://var/run/docker.sock",
        network_mode=DOCKER_NETWORK_NAME,
        auto_remove=True,
        mounts=COMMON_MELTANO_MOUNTS,
        mount_tmp_dir=False,
        working_dir=CONTAINER_MELTANO_PATH
    )

    # Tarefa 5: Carregar os CSVs (gerados nas etapas 1 e 2) para o Postgres de destino
    load_to_postgres = DockerOperator(
        task_id='carregamento_postgres',
        image=MELTANO_DOCKER_IMAGE,
        command="bash -c \""  
            "meltano config tap-csv-latest set csv_files_definition /opt/meltano/config/tap-csv-latest.json && "  # First command
            "meltano el tap-csv-latest target-postgres"  
            "\"", 
        mounts=COMMON_MELTANO_MOUNTS,
        working_dir=CONTAINER_MELTANO_PATH,
        network_mode=DOCKER_NETWORK_NAME,
        auto_remove=True,
        mount_tmp_dir=False,
        environment={}
    )

    # Tarefa 6: Validar os dados carregados no Postgres de destino
    validate_data_in_postgres = PostgresOperator(
        task_id='validar_dados_carregados',
        postgres_conn_id='postgres_target_conn',
        sql="""
            SELECT
                o.order_id AS ID_Pedido,
                o.order_date AS Data_Pedido,
                o.customer_id AS ID_Cliente,
                od.product_id AS ID_Produto,
                od.unit_price AS Preco_Unitario,
                od.quantity AS Quantidade,
                od.discount AS Desconto
            FROM
                orders o
            JOIN
                order_details od ON o.order_id = od.order_id
        """,
    )

    # Definição das Dependências (Fluxo da DAG)
    extract_postgres >> extract_csv >> generate_csv_config >> load_to_postgres >> validate_data_in_postgres







