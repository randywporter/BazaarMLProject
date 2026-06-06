CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS market_snapshots (
    time timestamptz NOT NULL,

    source TEXT NOT NULL,

    item_id TEXT,

    buy_summary JSONB NOT NULL,
    sell_summary JSONB NOT NULL,

    exact_delta_price NUMERIC,

    percent_margin_price NUMERIC,

    buy_price NUMERIC,
    sell_price NUMERIC,
    delta_price NUMERIC,

    buy_volume BIGINT,
    sell_volume BIGINT,
    delta_volume BIGINT,

    buy_moving_week BIGINT,
    sell_moving_week BIGINT,
    delta_moving_week BIGINT,

    raw JSONB NOT NULL
);

SELECT create_hypertable(
    'market_snapshots',
    'time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_item
ON market_snapshots(item_id);

CREATE INDEX IF NOT EXISTS idx_time
ON market_snapshots(time DESC);

CREATE INDEX IF NOT EXISTS idx_raw_gin
ON market_snapshots
USING GIN(raw);