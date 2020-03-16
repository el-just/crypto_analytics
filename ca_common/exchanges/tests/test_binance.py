# -*- coding: utf-8 -*-
"""
Testing Binance availability
"""

import pytest
import asyncio
import aiohttp

import os
import sys
import platform

delimiter = '/' if platform.system() in ('Linux', 'Darwin') else '\\'
current_path = os.path.dirname(os.path.abspath(__file__)).split(delimiter)
sys.path.append(delimiter.join(current_path[:-1]))
sys.path.append(delimiter.join(current_path[:-3]))

from binance import Binance

class TestBinance:
    exchange = Binance()

    @pytest.mark.asyncio
    async def test_connection(self):
        """
            Check if Binance available
        """

        response = await self.exchange.ping()
        assert type(response) == dict

    @pytest.mark.asyncio
    async def test_exchange_info(self):
        """
            Check exchange info
        """

        exchange_info = await self.exchange.get_info()
        assert 'symbols' in exchange_info.keys()

    @pytest.mark.asyncio
    async def test_symbols(self):
        """
            Check symbols
        """

        symbols = await self.exchange.get_symbols()
        assert len(symbols) > 0
