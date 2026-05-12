# ✈️ Brazilian Flights Pipeline

🌐 **API ao vivo:** https://brazilian-flights-pipeline.onrender.com/docs

Pipeline de dados end-to-end para análise de voos regulares brasileiros, utilizando dados públicos da ANAC (Agência Nacional de Aviação Civil).

## 🏗️ Arquitetura

```
ANAC (dados públicos)
        ↓
   Apache Airflow          ← orquestração e agendamento
        ↓
  Databricks Bronze        ← ingestão raw (CSV → Delta Table)
        ↓
  Databricks Silver        ← limpeza e tipagem (dbt Core)
        ↓
  Databricks Gold          ← agregações analíticas (dbt Core)
        ↓
     FastAPI               ← API REST para consumo dos dados
```

## 🛠️ Stack

| Ferramenta | Uso |
|---|---|
| Python 3.12 | linguagem principal |
| Apache Airflow 2.9 | orquestração das DAGs |
| Docker | ambiente local do Airflow |
| Databricks Free Edition | processamento e armazenamento (Delta Lake + Unity Catalog) |
| dbt Core 1.11 | transformações SQL (Silver e Gold) |
| FastAPI | API REST para exposição dos dados |
| GitHub | versionamento e CI/CD |

## 📊 Dados

Fonte: [ANAC — Voo Regular Ativo (VRA)](https://sistemas.anac.gov.br/dadosabertos)

- **Período:** 2022 a 2026
- **Volume:** ~102.000 registros
- **Campos:** companhia aérea, número do voo, aeródromos de origem/destino, horários previstos e reais, situação do voo

## 🗂️ Estrutura do Projeto

    brazilian-flights-pipeline/
    ├── airflow/dags/bronze_anac_vra.py   # DAG de ingestão Bronze
    ├── dbt/brazilian_flights/
    │   ├── models/silver/stg_vra.sql     # limpeza e tipagem
    │   ├── models/gold/agg_airline_performance.sql
    │   └── macros/generate_schema_name.sql
    ├── api/main.py                        # FastAPI
    ├── docker-compose.yaml
    └── .env                               # não versionado

## 🚀 Como rodar localmente

### Pré-requisitos
- Docker e Docker Compose
- Python 3.12+
- Conta no Databricks Free Edition

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/brazilian-flights-pipeline.git
cd brazilian-flights-pipeline
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# edite o .env com suas credenciais do Databricks
```

### 3. Suba o Airflow
```bash
docker compose up airflow-init
docker compose up -d
```
Acesse: http://localhost:8080 (admin/admin)

### 4. Configure o dbt
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dbt-databricks
cd dbt/brazilian_flights
dbt debug    # valida a conexão
dbt run      # executa os models
```

### 5. Suba a API
```bash
pip install fastapi uvicorn databricks-sql-connector python-dotenv
cd api
uvicorn main:app --reload --port 8000
```
Acesse: http://localhost:8000/docs

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | health check |
| GET | `/airlines` | lista todas as companhias aéreas |
| GET | `/performance?airline=GLO&year=2024` | performance por companhia e ano |
| GET | `/performance/summary?year=2024` | resumo agregado por companhia |

## 🏅 Medallion Architecture

**Bronze** — dados brutos ingeridos da ANAC sem transformação, armazenados como Delta Table em `workspace.bronze.vra`

**Silver** — dados limpos com tipos corretos, colunas padronizadas em inglês e métricas calculadas (`departure_delay_min`, `arrival_delay_min`) em `workspace.silver.stg_vra`

**Gold** — agregações analíticas por companhia, ano e mês com taxas de cancelamento, atraso médio e percentual de pontualidade em `workspace.gold.agg_airline_performance`

## 📈 Insights dos dados

- **Azul** é a companhia com maior volume de voos domésticos
- **TAP** apresenta consistentemente os maiores atrasos médios entre as internacionais
- Taxa de cancelamento média do mercado doméstico: ~2%
- Meses de janeiro e julho concentram os maiores volumes de voos

## 🔍 Exemplos de uso da API

A API está disponível em: **https://brazilian-flights-pipeline.onrender.com**

> ⚠️ O plano gratuito do Render pode demorar até 50 segundos na primeira requisição após inatividade. Aguarde e tente novamente.

### Listar todas as companhias aéreas
GET https://brazilian-flights-pipeline.onrender.com/airlines

### Performance de uma companhia em um ano específico
GET https://brazilian-flights-pipeline.onrender.com/performance?airline=GLO&year=2024

### Comparar todas as companhias em 2024
GET https://brazilian-flights-pipeline.onrender.com/performance/summary?year=2024

### Códigos ICAO das principais companhias brasileiras

| Código | Companhia |
|---|---|
| GLO | Gol |
| AZU | Azul |
| TAM | LATAM |
| ACN | Passaredo |
| PTB | MAP Linhas Aéreas |

### Exemplo de resposta — `/performance/summary?year=2024`

```json
{
  "data": [
    {
      "airline_icao": "AZU",
      "total_flights": 8542,
      "avg_cancellation_rate": 0.85,
      "avg_departure_delay": 24.3,
      "avg_delay_rate": 18.2
    }
  ]
}
```

## 👤 Autor

Desenvolvido por **Jheysson Douglas**  
Analytics Engineer com experiência em Airflow, Databricks, PySpark, dbt e SQL.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/jheyssondouglas/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/JheyssonDouglas)