# ETL Airflow Pipeline — Cryptocurrency Market Data

An Apache Airflow-based ETL pipeline that collects daily cryptocurrency market data from the [CoinGecko API](https://www.coingecko.com/en/api) and stores it in PostgreSQL. The entire stack runs in Docker.

## Architecture

```
CoinGecko API  →  Extract  →  Transform (pandas)  →  Load (PostgreSQL)
                                                          ↑
                                               Upsert on conflict (id)
```

The pipeline runs **daily** and fetches the top 10 cryptocurrencies by market cap (price, market cap, total volume).

## Tech Stack

| Component | Version |
|-----------|---------|
| Apache Airflow | 2.9.1 |
| Python | 3.12 |
| PostgreSQL | 15 |
| pandas | latest |
| psycopg2 | latest |

## Project Structure

```
etl-airflow-pipeline/
├── dags/
│   └── coingecko.py       # ETL DAG: extract → transform → load
├── plugins/               # Custom Airflow operators (empty, reserved)
├── logs/                  # Airflow task execution logs (git-ignored)
├── docker-compose.yml     # Orchestrates postgres, scheduler, webserver
├── dockerfile             # Airflow image with project dependencies
├── requirements.txt       # pandas, psycopg2-binary
├── .env                   # Local environment variables (git-ignored)
└── .env.example           # Template for .env
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your values. At minimum, generate a Fernet key for Airflow:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the output into `AIRFLOW__CORE__FERNET_KEY` in `.env`.

### 2. Start the stack

```bash
docker-compose up -d
```

On the first run, the `airflow-init` service initialises the database and creates the admin user. Wait for it to complete before using the UI.

### 3. Open the Airflow UI

Navigate to [http://localhost:8080](http://localhost:8080) and log in with the credentials from `.env` (defaults: `admin` / `admin`).

### 4. Enable and run the DAG

1. Find `coingecko_etl` in the DAG list.
2. Toggle it **On**.
3. Trigger a manual run or wait for the daily schedule (midnight UTC).

### 5. Stop the stack

```bash
docker-compose down
```

To also remove volumes (wipes the database):

```bash
docker-compose down -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `airflow` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `airflow` | PostgreSQL password |
| `POSTGRES_DB` | `coingecko` | Database name |
| `POSTGRES_HOST` | `postgres` | Hostname (must match the Compose service name) |
| `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` | — | Full SQLAlchemy connection string for Airflow metadata |
| `AIRFLOW__CORE__EXECUTOR` | `LocalExecutor` | Airflow executor type |
| `AIRFLOW__CORE__FERNET_KEY` | — | Encryption key for sensitive data (**required**) |
| `AIRFLOW_WWW_USER_USERNAME` | — | Airflow UI username |
| `AIRFLOW_WWW_USER_PASSWORD` | —| Airflow UI password |

## DAG: `coingecko_etl`

| Property | Value |
|----------|-------|
| Schedule | `@daily` (00:00 UTC) |
| Start date | 2024-01-01 |
| Catchup | Disabled |
| Retries | 3 × 5 min delay |

### Tasks

| Task | What it does |
|------|-------------|
| `extract` | GET `https://api.coingecko.com/api/v3/coins/markets` — top 10 coins by market cap in USD |
| `transform` | Selects `id`, `name`, `symbol`, `current_price`, `market_cap`, `total_volume`; adds `fetched_at` timestamp |
| `load` | Creates `Coins` table if absent; upserts rows keyed on `id`, updating price and volume columns |

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS Coins (
    id           TEXT PRIMARY KEY,
    name         TEXT,
    symbol       TEXT,
    current_price NUMERIC,
    market_cap   NUMERIC,
    total_volume NUMERIC,
    fetched_at   TIMESTAMP
);
```
