# -*- coding: utf-8 -*-
"""
Main testing scenarios

High-Level tests. Provide assurance that api and listener up and working
    + mass execution test
"""

import pytest
import urllib
import aiohttp
import asyncio

class TestMain:
    @pytest.mark.asyncio
    async def test_api_klines(self):
        """
            Testing availablility of api klines method
        """

        params = {
                "exchange": 'binance',
                "symbol": 'btcusdt',
                "interval": '1m',
                "limit": 500,
                }
        uri = 'http://localhost:6543/api/v1/klines?{query}'.format(
                query=urllib.parse.urlencode(params))
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                response = await resp.json()

        assert len(response)

    @pytest.mark.asyncio
    async def test_listener_connection(self):
        """
            Testing availablility of listener service
        """

        uri = 'http://localhost:6542/api/v1/ping'
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                response = await resp.json()

        assert response["status"]

    @pytest.mark.asyncio
    async def test_symbols_klines_loading(self):
        """
            Testing mass load data by symbols in clickhouse
        """

        params = {
                "exchange": 'binance',
                }
        uri = 'http://localhost:6543/api/v1/load_symbols_klines?{query}'.format(
                query=urllib.parse.urlencode(params))
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                response = await resp.json()

        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_api_mass_execution(self):
        """
            Testing mass rest execution. Trying not to overhead limits
        """

        params = {
                "exchange": 'binance',
                "symbol": 'btcusdt',
                "interval": '1m',
                "limit": 1,
                "new": True,
                }
        uri = 'http://localhost:6543/api/v1/klines?{query}'.format(
                query=urllib.parse.urlencode(params))

        async def request():
            async with aiohttp.ClientSession() as session:
                async with session.get(uri) as resp:
                    response = await resp.json()

        for i in range(10):
            await asyncio.gather(*[request() for i in range(100)])
