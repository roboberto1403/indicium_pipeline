# ./meltano/Dockerfile
FROM meltano/meltano:latest

# Copia o script de entrypoint customizado para dentro da imagem
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
# Torna o script executável DENTRO da imagem
RUN chmod +x /usr/local/bin/entrypoint.sh

# Define o diretório de trabalho dentro do contêiner
WORKDIR /opt/meltano

# Define o entrypoint para o seu script customizado
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Define um comando padrão (pode ser sobrescrito pelo DockerOperator)
CMD ["bash"]
