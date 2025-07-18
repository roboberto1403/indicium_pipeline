<img width="647" height="513" alt="image" src="https://github.com/user-attachments/assets/14c64525-8cef-44f0-b17c-b83ab7815724" />
# Projeto Indicium Data Pipeline

Este projeto implementa um pipeline de dados para extrair informações de um banco de dados PostgreSQL (Northwind) e um arquivo CSV (`order_details`), salvá-los no disco local e, em seguida, carregá-los em um banco de dados PostgreSQL de destino. A orquestração é feita com Apache Airflow e a movimentação de dados com Meltano, tudo conteinerizado com Docker Compose.

---

## 📌 Tecnologias Utilizadas

- **Apache Airflow**: Orquestração de workflows.
- **Meltano**: Extração e carregamento de dados (ELT).
- **PostgreSQL**: Banco de dados fonte e destino.
- **Docker & Docker Compose**: Conteinerização e orquestração.
- **WSL2**: Ambiente de desenvolvimento.

---

## ⚙️ Pré-requisitos

Certifique-se de ter instalado:

- Docker Desktop (com backend WSL2 habilitado)
- WSL2 (com uma distribuição Linux instalada)
- Git
- Make

---

## 🚀 Como Rodar o Projeto

### 1. Clonar o Repositório

```bash
git clone https://github.com/roboberto1403/indicium_pipeline.git
cd indicium_pipeline
```
### 2. Configuração Inicial
Antes de iniciar, crie ou edite o arquivo .env na raiz do projeto com as seguintes variáveis:

```bash
POSTGRES_USER_DESTINO=seu_usuario_destino
POSTGRES_PASSWORD_DESTINO=sua_senha_destino
POSTGRES_DB_DESTINO=seu_banco_destino
```
Para configurar o ambiente automaticamente, execute:

```bash
make setup
```
Esse comando executa o script setup.sh, que detecta o IP do host e configura os arquivos .env necessários para o projeto e o Meltano.

### 3. Iniciar os Serviços

```bash
make start
```
Internamente, esse comando executa:

```bash
sudo docker compose up -d --build --force-recreate
```
Isso iniciará os contêineres do PostgreSQL (fonte e destino) e do Airflow. O banco db_source será populado automaticamente com northwind.sql na primeira execução (ou após remoção dos volumes).

Aguarde alguns minutos até que todos os serviços estejam prontos.

### 4. Acessar e Executar o Pipeline no Airflow
Acesse a interface do Airflow: 

🔗 http://localhost:8080

- Login: `airflow`
- Senha: `airflow`

Na UI do Airflow:

1. Localize o DAG `northwind`
2. Ative o DAG (toggle switch)
3. Clique em "Play" (Trigger DAG)

## 🔁 Diagrama do Fluxo ELT
O fluxo completo do pipeline de dados pode ser visualizado a seguir:

<img width="647" height="513" alt="image" src="https://github.com/user-attachments/assets/14c64525-8cef-44f0-b17c-b83ab7815724" />

### 5. Verificação e Evidência

## 📁 Verifique os dados locais
Os arquivos .parquet estarão organizados da seguinte forma:

```bash
/data/postgres/{table}/{YYY-MM-DD}/file.csv
/data/csv/{table}/{YYY-MM-DD}/file.csv
```

## 🧾 Uma evidência é gerada na última etapa da DAG (validate_data_in_postgres), a qual roda o seguinte comando SQL:

```bash
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
```
Os dados advindos da tarefa podem ser conferidos na aba XCom 

### 6. Parar e Limpar os Serviços

Para parar os serviços:
```bash
make down
```
Para parar e remover volumes/dados completamente:
```bash
make clean
```

### 📬 Contato

Caso tenha dúvidas ou sugestões, fique à vontade para me contatar pelo meu email [lrbf@cin.ufpe.br](mailto:lrbf@cin.ufpe.br). 
