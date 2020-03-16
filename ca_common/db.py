# -*- coding: utf-8 -*-
"""
DB entities
"""

from collections import namedtuple

Kline = namedtuple('Kline', [
    "exchange",
    "symbol",
    "open_timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_timestamp",
    "quote_volume",
    "trades",
    "taker_base_volume",
    "taker_quote_volume",
    "ignore",
    ])
