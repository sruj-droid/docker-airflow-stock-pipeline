CREATE TABLE IF NOT EXISTS stock_data (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(16) NOT NULL,
  price NUMERIC,
  volume BIGINT,
  fetched_at TIMESTAMP DEFAULT now()
);

