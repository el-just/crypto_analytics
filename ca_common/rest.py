# -*- coding: utf-8 -*-
"""
Module for Rest requests

Sending get requests with params
"""

import aiohttp
import urllib

class Rest:
    _uri = None

    def __init__(self, uri):
        self._uri = uri if uri[-1] != '/' else uri[:-1]

    async def get(self, route, params=None):
        """
            Public get method
        """

        params = self._remove_nulls(params)
        uri = '{uri}/{route}?{query}'.format(
                uri=self._uri,
                route=route,
                query=urllib.parse.urlencode(params),
                )

        return await self._send(method='get', uri=uri)

    def _remove_nulls(self, params):
        """
            Removes None params from params
        """

        if params is not None:
            return {key:value for key, value in params.items() if value is not None}

        return {}

    async def _send(self, method, uri):
        """
            Main method for send requests
        """

        response = {"message": None, "headers": None}

        async with aiohttp.ClientSession() as session:
            rest_call = getattr(session, method)
            async with rest_call(uri) as resp:
                response["message"] = await resp.text()
                response["headers"] = resp.headers

        return response
