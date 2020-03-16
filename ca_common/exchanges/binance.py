# -*- coding: utf-8 -*-
"""
Binance entry point

Aggregates operations with binance
"""

import json
import asyncio
import websockets
import time

from ca_common.rest import Rest
from ca_common.clickhouse import Clickhouse
from ca_common.db import Kline


class Binance:
    __uri = 'https://api.binance.com/api/v3/'
    __ws_uri = 'wss://stream.binance.com:9443/'
    __rest = None
    __retry_after = None
    __lock = None

    __weight = 0

    clickhouse = None

    def __init__(self):
        self.__rest = Rest(uri=self.__uri)
        self.__lock = asyncio.Lock()
        self.clickhouse = Clickhouse()

    async def __execute(self, route, params=None):
        """
            Executing rest operations. Locking if over limits
        """

        response = None

        async with self.__lock:
            if self.__retry_after is not None:
                await asyncio.sleep(self.__retry_after)

        response = await self.__rest.get(route=route, params=params)
        self.__retry_after = response["headers"].get('retry-after', None)
        self.__retry_after = int(self.__retry_after) or 1 \
                if self.__retry_after is not None else None

        if int(response["headers"].get('x-mbx-used-weight', 1)) > 429:
            if self.__retry_after is None or self.__retry_after < 1:
                self.__retry_after = 1

        print(response["headers"])

        return json.loads(response["message"])

    async def ping(self):
        """
            Check if Binance online
        """

        return await self.__execute('ping')

    async def get_info(self):
        """
            Get Binance info
        """

        return await self.__execute('exchangeInfo')

    async def get_symbols(self):
        """
            Get list of available symbols
        """

        exchange_info = await self.get_info()

        return [symbol_info["symbol"] \
                for symbol_info in exchange_info["symbols"]]

    async def get_klines(self, symbol, interval,
            start_time=None, end_time=None, limit=None, new=False):
        """
            Getting klines. If data in clickhouse exists than using this data.
            In other case, requesting via rest
        """

        klines = None
        if not new:
            klines = await self.clickhouse.select_klines('binance',
                symbol, start_time, end_time, limit)

        if klines is None or len(klines) == 0:
            klines = await self.__execute('klines', params={
                    "symbol": symbol.upper(),
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    })
            print(klines)
            klines = [['binance', symbol.lower()] + kline for kline in klines]

        return klines

    def generate_id(self):
        """
            Generating id for websocket requests
        """

        return int((time.time()*1000)%10000000)

    async def stream(self):
        """
            Websocket stream
        """

        while True:
            try:
                symbols = await self.get_symbols()
                ws_path = (self.__ws_uri
                        + 'stream?streams='
                        + '/'.join(['%s@kline_1m'%symbol.lower() \
                            for symbol in symbols]))
                async with websockets.connect(ws_path) as websocket:
                    while True:
                        raw_data = json.loads(await websocket.recv())
                        kline = Kline(
                            'binance',
                            raw_data["data"]["s"].lower(),
                            raw_data["data"]["k"]["t"],
                            raw_data["data"]["k"]["o"],
                            raw_data["data"]["k"]["h"],
                            raw_data["data"]["k"]["l"],
                            raw_data["data"]["k"]["c"],
                            raw_data["data"]["k"]["v"],
                            raw_data["data"]["k"]["T"],
                            raw_data["data"]["k"]["q"],
                            raw_data["data"]["k"]["n"],
                            raw_data["data"]["k"]["V"],
                            raw_data["data"]["k"]["Q"],
                            raw_data["data"]["k"]["B"],)

                        await self.clickhouse.insert_klines([kline])
            except Exception as e:
                print (e)
