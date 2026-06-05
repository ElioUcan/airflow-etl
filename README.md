# ETL Pipeline — Airflow + CoinGecko

## 🛠️ Technologies
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## ✨ Features
- Daily ingestion of top 10 cryptocurrencies by market cap from the CoinGecko public API
- pandas transformation: selects relevant columns and adds a `fetched_at` timestamp
- PostgreSQL upsert keyed on `id` — safe to re-run without duplicating rows
- Airflow DAG with 3 retries (5-minute delay) for resilience against transient API failures
- Fully containerized with Docker Compose: Airflow scheduler, webserver, and PostgreSQL in one stack

## 🎯 Uses
Automated daily cryptocurrency market data pipeline demonstrating production-grade ETL orchestration with Apache Airflow. Built as project #1 in a Data/AI/MLOps engineering portfolio — the foundation that all subsequent projects build on.

## 🔧 Process
A single Airflow DAG (`coingecko_etl`) with three sequential tasks: `extract` calls the CoinGecko `/coins/markets` endpoint, `transform` cleans the response with pandas, and `load` upserts into PostgreSQL using `INSERT ... ON CONFLICT DO UPDATE`. Docker Compose runs Airflow's scheduler and webserver on top of a custom image that includes the project's Python dependencies.

## 💡 Learnings
- Upsert patterns (`ON CONFLICT DO UPDATE`) are essential for idempotent ETL — re-running a daily DAG should update existing rows, not create duplicates
- Airflow's `LocalExecutor` is sufficient for single-machine pipelines; `CeleryExecutor` only becomes necessary when parallelism across workers is needed
- Generating a Fernet key before initializing the Airflow database is mandatory — the init service fails silently without it

## ▶️ Running the project

```bash
cp .env.example .env
# generate Fernet key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# set AIRFLOW__CORE__FERNET_KEY and other variables

docker-compose up -d
```

Open the Airflow UI at **http://localhost:8080**, enable the `coingecko_etl` DAG, and trigger a manual run or wait for the daily schedule (midnight UTC).
