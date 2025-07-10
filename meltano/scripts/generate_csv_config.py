# ~/indicium_pipeline/meltano/scripts/generate_csv_config.py
import os
import json
from pathlib import Path
import datetime
import sys # Importar sys para stderr
import traceback # Importar traceback para imprimir o stack trace de erros

# --- Caminhos ABSOLUTOS DENTRO DO CONTAINER ---
CONTAINER_OUTPUT_DATA_BASE_PATH = Path("/opt/output_data")
CSV_OUTPUT_DIR = CONTAINER_OUTPUT_DATA_BASE_PATH / "csv"
POSTGRES_OUTPUT_DIR = CONTAINER_OUTPUT_DATA_BASE_PATH / "postgres"
MELTANO_CONFIG_DIR = Path("/opt/meltano/config")
OUTPUT_CONFIG_PATH = MELTANO_CONFIG_DIR / "tap-csv-latest.json"

# Garanta que o diretório de saída para a configuração existe
MELTANO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Definição das tabelas e suas chaves primárias
tables_config = {
    "order_details": { "keys": ["order_id", "product_id"], "source_dir": CSV_OUTPUT_DIR, "is_nested_by_entity": True },
    "categories": { "keys": ["category_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "products": { "keys": ["product_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "suppliers": { "keys": ["supplier_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "orders": { "keys": ["order_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "customers": { "keys": ["customer_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "employees": { "keys": ["employee_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "employee_territories": { "keys": ["employee_id", "territory_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "territories": { "keys": ["territory_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "region": { "keys": ["region_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "shippers": { "keys": ["shipper_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True },
    "us_states": { "keys": ["state_id"], "source_dir": POSTGRES_OUTPUT_DIR, "is_nested_by_entity": True }
}

# Lista para armazenar as definições de arquivos CSV para o tap-csv-latest
csv_files_definition = []

# Obter a data atual no formato YYYY-MM-DD
today = datetime.date.today().strftime("%Y-%m-%d")

for table_name, info in tables_config.items():
    source_dir_for_table = info["source_dir"]

    disk_entity_name = table_name
    if source_dir_for_table == POSTGRES_OUTPUT_DIR:
        # A documentação do tap-csv no Meltano Hub para o tap-csv-latest
        # indica que o 'entity' é o nome da entidade/tabela.
        # Se os nomes dos arquivos no disco são prefixados com 'public-',
        # mas a entidade no Meltano deve ser apenas o nome da tabela,
        # então 'disk_entity_name' deve ser o nome do diretório no disco.
        # No seu JSON original, você usou 'public-categories' como 'entity'.
        # Se 'entity' deve ser 'public-categories' e o diretório também,
        # então esta lógica está correta.
        disk_entity_name = f"public-{table_name}"
        if table_name == "customer_demographics":
            # Caso especial para customer_demographics se não tiver o prefixo 'public-'
            disk_entity_name = "customer_demographics"

    # Caminho para o diretório da entidade (ex: /opt/output_data/csv/order_details/)
    # Usamos a data atual para construir o caminho, assumindo que os arquivos são gerados diariamente
    entity_data_path = source_dir_for_table / disk_entity_name / today

    # Em vez de procurar o diretório de data mais recente, usamos a data atual
    # Isso assume que os arquivos CSV são sempre gerados para a data de execução da DAG
    # Se a lógica for diferente (ex: sempre o mais recente, independentemente da data),
    # você precisará reintroduzir a lógica de `max(os.path.getmtime)`.
    latest_date_dir = entity_data_path # Agora, este é o diretório da data atual

    # Garanta que o diretório de data exista antes de tentar listar arquivos
    if not latest_date_dir.is_dir():
        sys.stderr.write(f"ATENÇÃO: Diretório de data '{latest_date_dir}' não encontrado para '{disk_entity_name}'. Pulando esta entidade.\n")
        continue

    # Caminho completo para o arquivo 'file.csv' dentro do diretório de data
    absolute_file_path_in_container = latest_date_dir / "file.csv"

    # Verifica se o arquivo final 'file.csv' realmente existe
    if not absolute_file_path_in_container.is_file():
        sys.stderr.write(f"ATENÇÃO: Arquivo 'file.csv' não encontrado em {absolute_file_path_in_container}. Pulando esta entidade.\n")
        continue

    # Adiciona à definição de arquivos
    csv_files_definition.append({
        "entity": disk_entity_name, # O nome da entidade/tabela no Meltano
        "path": str(absolute_file_path_in_container), # Caminho absoluto para o arquivo CSV
        "keys": info["keys"], # Chaves primárias para a entidade
        "delimiter": ',',
        "encoding": "utf-8"
    })

# --- CORREÇÃO APLICADA AQUI ---
# Salvar a configuração no arquivo JSON
# O tap-csv-latest espera uma lista de objetos diretamente, não um dicionário com a chave "files".
try:
    # Garante que o diretório exista antes de tentar salvar
    OUTPUT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CONFIG_PATH, "w", encoding='utf-8') as f:
        # Agora, estamos despejando a lista diretamente
        json.dump(csv_files_definition, f, indent=2)
    
    if not csv_files_definition:
        sys.stderr.write("AVISO: A lista de arquivos CSV gerada está vazia. Verifique se os arquivos foram criados e as paths estão corretas.\n")
except Exception as e:
    sys.stderr.write(f"ERRO ao salvar o arquivo de configuração: {e}\n")
    sys.stderr.write(f"{traceback.format_exc()}\n")
    sys.exit(1) # Sai com erro se não conseguir salvar

# **CRÍTICO PARA XCOMS:** Imprimir SOMENTE o JSON serializado para stdout.
# Remova quaisquer outros 'print()' ou mensagens de log que vão para stdout.
# Agora, estamos imprimindo a lista diretamente para stdout.
print(json.dumps(csv_files_definition))


