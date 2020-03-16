# -*- coding: utf-8 -*-
"""
Clickhouse connector

Mini ORM for current db. Aggregates sync and async methods
"""

import aioch
import clickhouse_driver
import inspect

class Clickhouse:
    __sync = False
    __uri = 'clickhouse'
    __db = 'crypto_analytics'

    __client = None

    def __init__(self, uri=None, sync=False):
        """
            Setting up clickhouse driver
        """

        self.__uri = uri if uri is not None else self.__uri
        self.__sync = sync if sync is not None else self.__sync

        driver = aioch if sync == False else clickhouse_driver
        self.__client = driver.Client(self.__uri, database=self.__db)

    def __getattribute__(self, attr):
        """
            Choosing async or sync version of method
        """

        prop = super(Clickhouse, self).__getattribute__(attr)
        if inspect.iscoroutinefunction(prop) and self.__sync:
            return super(Clickhouse, self).__getattribute__('%s_sync'%attr)

        return prop

    async def execute(self, *args, **kwargs):
        """
            Proxy to driver execute
        """

        return await self.__client.execute(*args, **kwargs)

    async def ping(self):
        """
            Check if Clickhouse up
        """

        select = await self.__client.execute('SELECT 1')
        return len(select) > 0

    async def show_tables(self):
        """
            Check tables
        """

        return await self.__client.execute('SHOW TABLES')

    async def insert_klines(self, klines, table='klines'):
        """
            Insert klines
        """
        await self.__client.execute('''INSERT INTO %s VALUES'''%table, klines)

    async def select_klines(self, exchange=None, symbol=None,
            start_time=None, end_time=None, limit=None,
            table='klines'):
        """
            Method for quering in Klines
        """

        search_query = []
        if exchange is not None:
            search_query.append("exchange = '%s'"%exchange)
        if symbol is not None:
            search_query.append("symbol = '%s'"%symbol)
        if start_time is not None:
            search_query.append("open_timestamp >= %s"%start_time)
        if end_time is not None:
            search_query.append("close_timestamp <= %s"%end_time)

        if len(search_query) is not None:
            search_query = 'WHERE ' + ' AND '.join(search_query)
        else:
            search_query = ''

        limit_query = ''
        if limit is not None:
            limit_query = 'LIMIT %s'%limit

        query = '''
                SELECT * FROM {table}
                {search_query}
                ORDER BY open_timestamp DESC
                {limit_query}
            '''.format(table=table, search_query=search_query,
                    limit_query=limit_query)
        return await self.__client.execute(query)


#### Sync Functions
    def execute_sync(self, *args, **kwargs):
        return self.__client.execute(*args, **kwargs)

    def ping_sync(self):
        return len(self.__client.execute('SELECT 1')) > 0

    def show_tables_sync(self):
        return self.__client.execute('SHOW TABLES')

    def insert_klines_sync(self, klines, table='klines'):
        self.__client.execute('''INSERT INTO %s VALUES'''%table, klines)

    def select_klines_sync(self, table='klines'):
        return self.__client.execute('''SELECT * FROM %s'''%table)
