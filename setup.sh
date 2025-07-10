#!/bin/bash

echo "Detectando o IP da máquina host Windows no ambiente WSL2 (via gateway padrão)..."

HOST_IP=$(ip route show | grep default | awk '{print $3}' | head -1)

if [ -z "$HOST_IP" ]; then
    echo "ERRO: Não foi possível detectar o IP do gateway padrão do WSL2 automaticamente."
    echo "Por favor, insira o IP do seu host Windows manualmente no arquivo .env na raiz do projeto (ex: HOST_MACHINE_IP=192.168.X.Y)"
    exit 1
fi

echo "IP da máquina host Windows detectado: $HOST_IP"

# --- ATUALIZA O .env DA RAIZ ---
# Pega as credenciais de destino do .env da raiz antes de sobrescrever HOST_MACHINE_IP
# Se você já tem um .env na raiz, ele será usado. Caso contrário, estas variáveis podem ser vazias.
# Para garantir que elas sejam definidas, você pode pedir ao usuário para inserí-las no .env da raiz,
# ou até mesmo criar prompts no script. Por simplicidade, assumimos que já estão lá.
POSTGRES_USER_DESTINO=$(grep -E '^POSTGRES_USER_DESTINO=' .env | cut -d '=' -f2)
POSTGRES_PASSWORD_DESTINO=$(grep -E '^POSTGRES_PASSWORD_DESTINO=' .env | cut -d '=' -f2)
POSTGRES_DB_DESTINO=$(grep -E '^POSTGRES_DB_DESTINO=' .env | cut -d '=' -f2)
# Adiciona a leitura da porta de destino, ou assume 5432 se não estiver no .env
TARGET_POSTGRES_PORT=$(grep -E '^TARGET_POSTGRES_PORT=' .env | cut -d '=' -f2)
if [ -z "$TARGET_POSTGRES_PORT" ]; then
    TARGET_POSTGRES_PORT=5432
    echo "Aviso: TARGET_POSTGRES_PORT não encontrada no .env, usando a porta padrão 5432."
fi

# Atualiza HOST_MACHINE_IP no .env da raiz
sed -i '/^HOST_MACHINE_IP=/d' .env
echo "HOST_MACHINE_IP=$HOST_IP" >> .env

# --- NOVO: GERA E ADICIONA AIRFLOW_CONN_POSTGRES_TARGET_CONN AO .env DA RAIZ ---
# Remove qualquer linha AIRFLOW_CONN_POSTGRES_TARGET_CONN existente para evitar duplicatas
sed -i '/^AIRFLOW_CONN_POSTGRES_TARGET_CONN=/d' .env
# Constrói a string de conexão completa
AIRFLOW_CONN_STRING="postgresql://${POSTGRES_USER_DESTINO}:${POSTGRES_PASSWORD_DESTINO}@${HOST_IP}:${TARGET_POSTGRES_PORT}/${POSTGRES_DB_DESTINO}"
# Adiciona a nova string de conexão ao .env da raiz
echo "AIRFLOW_CONN_POSTGRES_TARGET_CONN=${AIRFLOW_CONN_STRING}" >> .env
echo "Arquivo .env na raiz do projeto atualizado com HOST_MACHINE_IP e AIRFLOW_CONN_POSTGRES_TARGET_CONN."

# --- ATUALIZA O .env DO MELTANO ---
MELTANO_ENV_FILE="./meltano/.env"

# Limpa o arquivo meltano/.env de variáveis de conexão antigas
sed -i '/^TARGET_POSTGRES_HOST=/d' "$MELTANO_ENV_FILE"
sed -i '/^TARGET_POSTGRES_PORT=/d' "$MELTANO_ENV_FILE"
sed -i '/^TARGET_POSTGRES_USER=/d' "$MELTANO_ENV_FILE"
sed -i '/^TARGET_POSTGRES_PASSWORD=/d' "$MELTANO_ENV_FILE"
sed -i '/^TARGET_POSTGRES_DATABASE=/d' "$MELTANO_ENV_FILE"

# Adiciona as novas variáveis ao meltano/.env
echo "TARGET_POSTGRES_HOST=$HOST_IP" >> "$MELTANO_ENV_FILE"
echo "TARGET_POSTGRES_PORT=$TARGET_POSTGRES_PORT" >> "$MELTANO_ENV_FILE" # Usa a variável lida/assumida
echo "TARGET_POSTGRES_USER=$POSTGRES_USER_DESTINO" >> "$MELTANO_ENV_FILE"
echo "TARGET_POSTGRES_PASSWORD=$POSTGRES_PASSWORD_DESTINO" >> "$MELTANO_ENV_FILE"
echo "TARGET_POSTGRES_DATABASE=$POSTGRES_DB_DESTINO" >> "$MELTANO_ENV_FILE"

echo "Arquivo meltano/.env atualizado com as configurações de destino."
echo "Agora, execute 'sudo docker-compose up -d --build --force-recreate' para iniciar seus serviços."
