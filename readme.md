# Dockerized Stock Market Data Pipeline (Airflow)

## Overview
This project implements a fully Dockerized data pipeline that retrieves stock
market data from Alpha Vantage, parses it, and stores it into a PostgreSQL database.
The pipeline is orchestrated using Apache Airflow.

This project meets all assignment requirements:
- Docker Compose for one-command setup
- Orchestrated DAG running hourly
- Error handling and missing data protection
- Secure environment variables
- Scalable and containerized architecture

## How to Run

### 1. Clone the repo
git clone <repo-url>
cd project/

### 2. Add environment variables
Create a `.env` file:
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=stocks
STOCK_API_KEY=YOUR_ALPHA_VANTAGE_KEY
FERNET_KEY=GENERATED_KEY

### 3. Start the pipeline
docker-compose up -d

### 4. Open Airflow UI
http://localhost:8080  
User: admin  
Pass: admin

Enable the DAG named: **stock_pipeline_dag**

## File Structure
- docker-compose.yml → container orchestration  
- dags/stock_pipeline_dag.py → Airflow pipeline  
- scripts/fetch_and_store.py → API + DB logic  
- README.md → setup instructions  

## Database Table
