# ETL Pipeline — Airflow + CoinGecko

## Technologies
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

<img width="1579" height="1336" alt="coinGecko-graph" src="https://github.com/user-attachments/assets/78a43f0b-eade-4dd8-9c13-d70ce02ffefa" />

## Features
- Daily ingestion of top 10 cryptocurrencies by market cap from the CoinGecko public API
- pandas transformation: selects relevant columns and adds a `fetched_at` timestamp
- PostgreSQL upsert keyed on `id` — safe to re-run without duplicating rows
- Airflow DAG with 3 retries (5-minute delay) for resilience against transient API failures
- Fully containerized with Docker Compose: Airflow 3.2.2 scheduler, API server, dag-processor, triggerer, and PostgreSQL in one stack

## Overview
Automated daily cryptocurrency market data pipeline demonstrating production-grade ETL orchestration with Apache Airflow. Built as project #1 in a Data/AI/MLOps engineering portfolio — the foundation that all subsequent projects build on.

## How it works
A single Airflow DAG (`coinGecko`) with three sequential tasks: `extract` calls the CoinGecko `/coins/markets` endpoint, `transform` cleans the response with pandas, and `load` upserts into PostgreSQL using `INSERT ... ON CONFLICT DO UPDATE`.

## Running the project

### 1. Configure environment variables

Create a `.env` file in the project root with the following variables:

```env
# PostgreSQL
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Airflow metadata database connection
# Format: postgresql+psycopg2://<user>:<password>@<host>/<db>
# The host must match the postgres service name in docker-compose.yml
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# Fernet key — used to encrypt sensitive values (connections, variables) stored in the
# Airflow metadata database. Must be set before running `airflow db migrate`.
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIRFLOW__CORE__FERNET_KEY=

# Secret key — used by the Airflow API server for Flask session cookies.
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
AIRFLOW__CORE__SECRET_KEY=

# JWT secret — used to sign tokens that task processes present to the execution API
# server when reporting status. The scheduler and API server must share this value;
# if it is missing, each service generates a random key at startup and task runs fail
# with "Signature verification failed".
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
AIRFLOW__API_AUTH__JWT_SECRET=

# Airflow web UI credentials
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
```

### 2. Start the stack

```bash
docker compose up -d
```

### 3. Trigger the DAG

Open the Airflow UI at **http://localhost:8080**, unpause the `coinGecko` DAG, and trigger a manual run or wait for the daily schedule (midnight UTC).

### 4. Verify the data

```bash
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c 'SELECT * FROM "Coins" LIMIT 5;'
```

## Learnings
- Upsert patterns (`ON CONFLICT DO UPDATE`) are essential for idempotent ETL — re-running a daily DAG should update existing rows, not create duplicates
- Airflow 3.x splits responsibilities across multiple services (`api-server`, `dag-processor`, `triggerer`) instead of a single webserver process
- The Fernet key, core secret key, and JWT secret must all be explicitly set and shared across every Airflow service — missing any one of them causes silent or cryptic failures
- `LocalExecutor` is sufficient for single-machine pipelines; `CeleryExecutor` is only needed when distributing tasks across multiple workers
