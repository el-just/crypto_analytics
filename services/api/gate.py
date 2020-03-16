# -*- coding: utf-8 -*-
"""
The main gate to route api requests

Aggregatest api logic
"""

from importlib import import_module
import asyncio

class Gate:
    __exchanges = None

    def __init__(self):
        self.__exchanges = {}

    def __get_exchange(self, exchange):
        """
            Getter for exchanges instances
        """

        if exchange not in self.__exchanges.keys():
            self.__exchanges[exchange] = getattr(
                import_module('ca_common.exchanges.%s'%exchange),
                exchange.capitalize())()

        return self.__exchanges[exchange]

    async def execute(self, entity, params):
        """
            Main entry point. Responsible for passing parameters and other
        """

        return await getattr(self, entity)(**params)

    async def klines(self, exchange, **params):
        """
            Klines endpoint
        """

        return await self.__get_exchange(exchange).get_klines(**params)

    async def load_symbols_klines(self, exchange):
        """
            Endpoint for loading symbols in clickhouse
        """

        exchange = self.__get_exchange(exchange)
        symbols = await exchange.get_symbols()

        klines = []
        while len(symbols) > 0:
            results = await asyncio.gather(
                    *[exchange.get_klines(symbol, '1m', limit=1, new=True) \
                            for symbol in symbols[0:100]])
            for result in results:
                klines.append(result[0])

            symbols = symbols[101:]

        await exchange.clickhouse.insert_klines(klines)

        return klines
