FROM python:3.12-slim

FROM apache/airflow:3.2.2

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

CMD ["python3", "coingecko.py"]