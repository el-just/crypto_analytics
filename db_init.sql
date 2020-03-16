CREATE DATABASE IF NOT EXISTS crypto_analytics;

CREATE TABLE IF NOT EXISTS crypto_analytics.klines (
    `exchange` String,
    `symbol` String,
    `open_timestamp` UInt64,
    `open` Decimal(30,8),
    `high` Decimal(30,8),
    `low` Decimal(30,8),
    `close` Decimal(30,8),
    `volume` Decimal(30,8),
    `close_timestamp` UInt64,
    `quote_volume` Decimal(30,8),
    `trades` UInt64,
    `taker_base_volume` Decimal(30,8),
    `taker_quote_volume` Decimal(30,8),
    `ignore` Decimal(30,8)
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(toDate(open_timestamp))
ORDER BY (exchange, symbol, open_timestamp, close_timestamp)
PRIMARY KEY (exchange, symbol, open_timestamp, close_timestamp);
