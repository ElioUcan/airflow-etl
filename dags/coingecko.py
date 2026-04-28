from datetime import datetime, timedelta
from airflow.decorators import dag, task
from requests import get
import pandas as pd
import psycopg2
import os


@dag(
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule="@daily",
    default_args={"retries": 3, "retry_delay": timedelta(minutes=5)},
)
def coingecko_etl():
    @task
    def extract():
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10}
        request = get(url, params=params)
        return request.json()

    @task
    def transform(raw_data):
        columns = [
            "id",
            "name",
            "symbol",
            "current_price",
            "market_cap",
            "total_volume",
        ]
        df_raw = pd.DataFrame(raw_data)
        df = df_raw[columns]
        df["fetched_at"] = datetime.now().isoformat()
        return df.to_dict(orient="records")

    @task
    def load(clean_data):
        print(f"Received {len(clean_data)} rows")
        try:
            with psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
            ) as conn:
                with conn.cursor() as cur:
                    print("Connected ✅")
                    cur.execute("""CREATE TABLE IF NOT EXISTS Coins (
                                id TEXT NOT NULL,
                                name TEXT NOT NULL,
                                symbol TEXT NOT NULL,
                                current_price FLOAT NOT NULL,
                                market_cap BIGINT NOT NULL,
                                total_volume BIGINT NOT NULL,
                                fetched_at TIMESTAMP NOT NULL,

                                CONSTRAINT pk_coin PRIMARY KEY(id));""")
                    print("Table created ✅")
                    for row in clean_data:
                        cur.execute(
                            """INSERT INTO Coins (id, name, symbol, current_price, market_cap, total_volume, fetched_at) VALUES (%s, %s, %s, %s, %s, %s, %s) 
                            ON CONFLICT (id) DO UPDATE SET
                            current_price= EXCLUDED.current_price,
                            market_cap=EXCLUDED.market_cap,
                            total_volume=EXCLUDED.total_volume;""",
                            (
                                row["id"],
                                row["name"],
                                row["symbol"],
                                row["current_price"],
                                row["market_cap"],
                                row["total_volume"],
                                row["fetched_at"],
                            ),
                        )
                conn.commit()
                print("Committed ✅")
        except Exception as e:
            print(f"Error: {e}")

    raw = extract()
    clean = transform(raw)
    load(clean)


coingecko_etl()
