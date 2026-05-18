# Dockerized Airflow Stock Data Pipeline

A containerized pipeline that uses **Apache Airflow** to schedule fetches from the **Alpha Vantage** API and load stock quotes into **PostgreSQL**.

## Overview

An Airflow DAG runs hourly and executes `scripts/fetch_and_store.py`, which calls Alpha VantageΓÇÖs `GLOBAL_QUOTE` endpoint for each configured symbol, parses the JSON response, and inserts rows into the `stock_data` table.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine + Compose (Linux)
- An [Alpha Vantage](https://www.alphavantage.co/) API key (free tier is fine)
- Ports **8080** (Airflow UI) and **5432** (Postgres) available on the host

## Quick start

### 1. Clone and configure environment

```bash
git clone <your-repo-url>
cd docker-airflow-stock-pipeline
cp .env.example .env
```

Edit `.env` and set all variables (see [Environment variables](#environment-variables) below).

### 2. Build and start services

```bash
docker compose up --build -d
```

Wait until containers are healthy (first run may take several minutes while the image builds and Airflow initializes the database).

### 3. Open Airflow and enable the DAG

1. Open [http://localhost:8080](http://localhost:8080)
2. Log in with username **`admin`** and password from `AIRFLOW_ADMIN_PASSWORD` in your `.env`
3. Toggle **fetch_stock_data** ON, or trigger a manual run from the DAG view

### 4. Verify data

Connect to Postgres on `localhost:5432` with the credentials from `.env`, then:

```sql
SELECT * FROM stock_data ORDER BY fetched_at DESC LIMIT 20;
```

Example using Docker:

```bash
docker compose exec postgres psql -U airflow -d airflow_db -c "SELECT symbol, price, volume, fetched_at FROM stock_data ORDER BY fetched_at DESC LIMIT 10;"
```

(Replace `airflow` / `airflow_db` if you changed `POSTGRES_USER` / `POSTGRES_DB`.)

## Environment variables

| Variable | Required | Used by | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | Yes | Postgres, Airflow, fetch script | Database user |
| `POSTGRES_PASSWORD` | Yes | Postgres, Airflow, fetch script | Database password |
| `POSTGRES_DB` | Yes | Postgres, Airflow, fetch script | Database name (metadata + `stock_data`) |
| `AIRFLOW_ADMIN_PASSWORD` | Yes | Airflow webserver | Password for UI user `admin` |
| `ALPHA_VANTAGE_API_KEY` | Yes | Fetch script | API key from Alpha Vantage |
| `STOCK_SYMBOLS` | Yes | Fetch script | Comma-separated tickers, e.g. `MSFT,AAPL,GOOGL` |
| `POSTGRES_HOST` | No | Fetch script | Set automatically in Compose (`postgres` in containers; default `postgres`) |
| `POSTGRES_PORT` | No | Fetch script | Default `5432` |

Docker Compose reads `.env` from the project root for `${VAR}` substitution. The **scheduler** also loads `.env` via `env_file` so task processes receive `ALPHA_VANTAGE_API_KEY` and `STOCK_SYMBOLS`.

### How to obtain each value

| Variable | How to get it |
|----------|----------------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | **You choose these.** Pick strong passwords for anything beyond local dev. Defaults in `.env.example` work for local testing. |
| `AIRFLOW_ADMIN_PASSWORD` | **You choose this.** Any secure string; used only for the Airflow UI (`admin` user). |
| `ALPHA_VANTAGE_API_KEY` | 1. Go to [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)<br>2. Enter email and request a free key<br>3. Copy the key into `.env` |
| `STOCK_SYMBOLS` | **You choose these.** US ticker symbols supported by Alpha Vantage (e.g. `AAPL`, `MSFT`). Separate multiple symbols with commas. |

**Security:** Never commit `.env` or share API keys. If a key was exposed, regenerate it on the Alpha Vantage site.

## Useful commands

```bash
# View logs
docker compose logs -f airflow-scheduler
docker compose logs -f airflow-webserver

# Stop stack
docker compose down

# Stop and remove DB volume (recreates schema from initdb/init.sql)
docker compose down -v

# Rebuild after dependency or Dockerfile changes
docker compose up --build -d
```

## Project structure

```
.
Γö£ΓöÇΓöÇ dags/
Γöé   ΓööΓöÇΓöÇ fetch_stock_data_dag.py   # Hourly DAG
Γö£ΓöÇΓöÇ scripts/
Γöé   ΓööΓöÇΓöÇ fetch_and_store.py        # API fetch + DB insert
Γö£ΓöÇΓöÇ initdb/
Γöé   ΓööΓöÇΓöÇ init.sql                  # stock_data table (first DB init only)
Γö£ΓöÇΓöÇ Dockerfile
Γö£ΓöÇΓöÇ docker-compose.yml
Γö£ΓöÇΓöÇ requirements.txt
Γö£ΓöÇΓöÇ .env.example
ΓööΓöÇΓöÇ .env                          # local only (not in git)
```

## Database schema

```sql
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    price NUMERIC,
    volume BIGINT,
    fetched_at TIMESTAMP DEFAULT now()
);
```

## How the pipeline works

1. The scheduler triggers `fetch_stock_data` on the cron in the DAG (`0 * * * *` = hourly).
2. The task runs `fetch_and_store.py` in a subprocess.
3. For each symbol in `STOCK_SYMBOLS`, the script calls Alpha Vantage, waits 12 seconds (rate-limit safety), then bulk-inserts into `stock_data`.
4. Task logs appear in the Airflow UI under the DAG run.

## Customization

- **Tickers:** edit `STOCK_SYMBOLS` in `.env`, then restart: `docker compose up -d`
- **Schedule:** edit `schedule_interval` in `dags/fetch_stock_data_dag.py`
- **Schema changes:** update `initdb/init.sql` and recreate the Postgres volume (`docker compose down -v`) if the DB already exists

## Notes

- Alpha Vantage free tier has strict rate limits (about 5 requests/minute, 500/day). The script sleeps 12 seconds between symbols.
- If the DAG fails with ΓÇ£API key not setΓÇ¥, confirm `.env` exists and `airflow-scheduler` was restarted after editing it.
- `initdb/init.sql` runs only when the Postgres data volume is first created.
- Rebuild containers after changing `requirements.txt`, the Dockerfile, or environment variables loaded at build time.

## Technology stack

- Apache Airflow 2.10 (LocalExecutor)
- Python 3.11 (`requests`, `psycopg2-binary`, `python-dotenv`)
- PostgreSQL 15
- Docker Compose
