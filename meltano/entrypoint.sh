#!/bin/bash
set -e # Sai imediatamente se um comando falhar

echo "Running meltano install..."
meltano install || { echo "Meltano install failed. Check logs above."; exit 1; }

echo "Meltano install completed. Executing command: $*"

# Criar o diretório de configuração do Airflow se não existir
mkdir -p /opt/airflow/dags

# Criar as pastas de output para o Meltano (se não existirem)
# Elas são mapeadas via volume mount para o seu host em ~/indicium_pipeline/data/
mkdir -p /opt/output_data/postgres
mkdir -p /opt/output_data/csv

# Ajustar permissões (garantir que o usuário do Meltano possa escrever,
# mesmo que já esteja rodando como root, é uma boa prática)
chmod -R 777 /opt/output_data/postgres
chmod -R 777 /opt/output_data/csv

# Executa o comando que foi passado para o DockerOperator (ex: meltano el tap-postgres target-csv-postgres)
exec "$@"