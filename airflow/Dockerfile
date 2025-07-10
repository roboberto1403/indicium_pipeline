# ~/indicium_pipeline/airflow/Dockerfile
FROM apache/airflow:2.8.1-python3.10

USER root 

# ESTA É A LINHA CRUCIAL: SUBSTITUA PELO SEU GID: 108
ARG DOCKER_GID=108

# Cria um grupo 'docker' no container com o GID do host (se já não existir)
RUN groupadd -g $DOCKER_GID docker || true
# Adiciona o usuário 'airflow' a este grupo 'docker'
RUN usermod -aG docker airflow

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Mantenha este comando ajustado para lidar com o PID stale e chamar 'airflow webserver'
CMD ["bash", "-cx", "rm -f /opt/airflow/airflow-webserver.pid && exec airflow webserver"]