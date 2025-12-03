#!/usr/bin/env python3
# scripts/fetch_and_store.py
import os
import time
import logging
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("fetch_and_store")

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
SYMBOLS = [s.strip() for s in os.getenv("STOCK_SYMBOLS", "MSFT").split(",") if s.strip()]

POSTGRES = {
    "user": os.getenv("POSTGRES_USER", "airflow"),
    "password": os.getenv("POSTGRES_PASSWORD", "airflow_pass"),
    "db": os.getenv("POSTGRES_DB", "airflow_db"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
}

BASE_URL = "https://www.alphavantage.co/query"

def fetch_symbol(symbol):
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
    try:
        r = requests.get(BASE_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        volume = quote.get("06. volume")
        timestamp = quote.get("07. latest trading day")
        if not price:
            LOG.warning("No price in response for %s. Response: %s", symbol, data)
            return None
        try:
            price_val = float(price)
        except Exception:
            price_val = None
        try:
            volume_val = int(volume) if volume else None
        except Exception:
            volume_val = None
        try:
            fetched_at = datetime.strptime(timestamp, "%Y-%m-%d") if timestamp else datetime.utcnow()
        except Exception:
            fetched_at = datetime.utcnow()
        return {"symbol": symbol, "price": price_val, "volume": volume_val, "fetched_at": fetched_at}
    except Exception as e:
        LOG.exception("Failed to fetch %s: %s", symbol, e)
        return None

def persist_rows(rows):
    if not rows:
        LOG.info("No rows to persist.")
        return
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES["db"],
            user=POSTGRES["user"],
            password=POSTGRES["password"],
            host=POSTGRES["host"],
            port=POSTGRES["port"]
        )
        cur = conn.cursor()
        sql = """
            INSERT INTO stock_data (symbol, price, volume, fetched_at)
            VALUES %s
        """
        values = [(r["symbol"], r["price"], r["volume"], r["fetched_at"]) for r in rows]
        execute_values(cur, sql, values)
        conn.commit()
        cur.close()
        LOG.info("Inserted %d rows", len(rows))
    except Exception:
        LOG.exception("DB insert failed")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def run():
    if not API_KEY:
        LOG.error("API key not set. Set ALPHA_VANTAGE_API_KEY in environment.")
        return
    results = []
    for sym in SYMBOLS:
        LOG.info("Fetching %s", sym)
        r = fetch_symbol(sym)
        if r:
            results.append(r)
        time.sleep(12)  # keep safe with rate limits
    rows = [r for r in results if r.get("price") is not None]
    persist_rows(rows)
    return rows

if __name__ == "__main__":
    run()
