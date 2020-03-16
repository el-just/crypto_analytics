# -*- coding: utf-8 -*-
"""
Testing main clickhouse functional
"""

import pytest
import asyncio
import aiohttp
import uvloop
from decimal import Decimal

import os
import sys
import platform

import random
import string

delimiter = '/' if platform.system() in ('Linux', 'Darwin') else '\\'
current_path = os.path.dirname(os.path.abspath(__file__)).split(delimiter)
sys.path.append(delimiter.join(current_path[:-1]))

from clickhouse import Clickhouse

@pytest.fixture(scope="module")
def clickhouse_client():
    """
        Preparing driver
    """

    return Clickhouse(uri='localhost', sync=True)

@pytest.fixture()
def klines(clickhouse_client):
    """
        Custom klines data
    """

    return [
        [
            'binance',
            'btcusdt',
            1499040000000,
            "0.01634790",
            "0.80000000",
            "0.01575800",
            "0.01577100",
            "148976.11427815",
            1499644799999,
            "2434.19055334",
            308,
            "1756.87402397",
            "28.46694368",
            "17928899.62484339"
        ],
    ]

@pytest.fixture()
def klines_table(clickhouse_client):
    """
        Temporary Klines table
    """

    name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    clickhouse_client.execute('''
            CREATE TABLE %s (
                `exchange` String,
                `symbol` String,
                `open_timestamp` UInt64,
                `open` Decimal(30, 8),
                `high` Decimal(30, 8),
                `low` Decimal(30, 8),
                `close` Decimal(30, 8),
                `volume` Decimal(30, 8),
                `close_timestamp` UInt64,
                `quote_volume` Decimal(30, 8),
                `trades` UInt64,
                `taker_base_volume` Decimal(30, 8),
                `taker_quote_volume` Decimal(30, 8),
                `ignore` Decimal(30, 8)
            ) ENGINE = Memory
            '''%name)

    yield name
    clickhouse_client.execute('''DROP TABLE %s'''%name)

class TestClickhouse:
    def test_connection(self, clickhouse_client):
        """
            Testing that clickhouse is up
        """

        assert clickhouse_client.ping()

    def test_klines_table_exists(self, clickhouse_client):
        """
            Testing that klines table exists
        """

        table_rows = clickhouse_client.show_tables()
        assert 'klines' in [table_row[0] for table_row in table_rows]

    def test_klines_operations(self, clickhouse_client, klines_table, klines):
        """
            Testing that insert/select works
        """

        clickhouse_client.insert_klines(klines, table=klines_table)

        klines = clickhouse_client.select_klines(table=klines_table)
        assert len(klines) == 1
