Dockerized Airflow Stock Data Pipeline

This project implements a fully containerized data pipeline using Apache Airflow, PostgreSQL, and Docker Compose. The pipeline retrieves stock market data from the Alpha Vantage API, processes the JSON response, and loads the extracted values into a PostgreSQL table on a scheduled basis.

Overview

The pipeline is orchestrated through an Airflow DAG that executes at a configurable interval. A Python script fetches stock price and volume information from the API, applies basic validation, and stores the processed data in a PostgreSQL database. The entire system runs inside Docker containers, ensuring reproducibility and portability across environments.

Features

Automated scheduling using Apache Airflow

Data retrieval from Alpha Vantage (GLOBAL_QUOTE endpoint)

JSON parsing and error-handled data extraction

Storage of stock data in a PostgreSQL table

Containerized deployment using Docker Compose

Environment-based configuration for API keys and credentials

Technology Stack

Apache Airflow (LocalExecutor)

Python (requests, psycopg2)

PostgreSQL

Docker and Docker Compose

Alpha Vantage API

Project Structure
.
├─ dags/
│  └─ fetch_stock_data_dag.py
├─ scripts/
│  └─ fetch_and_store.py
├─ initdb/
│  └─ init.sql
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ .env.example

Setup Instructions

Clone the repository locally.

Create a .env file based on .env.example and provide your Alpha Vantage API key and database credentials.

Build and start the containers:

docker compose up --build -d


Access the Airflow web UI at:

http://localhost:8080


Default credentials can be updated in the .env file.

Enable the fetch_stock_data DAG in the Airflow UI or trigger it manually.

Database Table

The PostgreSQL database initializes with the following table:

CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(16),
    price NUMERIC,
    volume BIGINT,
    fetched_at TIMESTAMP DEFAULT now()
);

How the Pipeline Works

Airflow triggers the DAG at the scheduled interval.

The Python script calls the Alpha Vantage API and retrieves stock market data.

The script validates and parses the JSON response.

Extracted records are inserted into the stock_data table.

Logs and task history can be monitored through Airflow.

Customization

Modify STOCK_SYMBOLS in the .env file to change the list of tickers.

Adjust the schedule in fetch_stock_data_dag.py using cron syntax.

Extend the pipeline with additional transformations or destinations.

Notes

API rate limits apply on the free tier of Alpha Vantage. The script includes basic throttling logic.

Ensure that Docker Desktop is running before launching the pipeline.

Rebuild containers whenever dependencies or environment variables are updated.
