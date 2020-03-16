# -*- coding: utf-8 -*-
"""
Routes for aiohttp

HTTP Routes
"""

import aiohttp
import json

async def api(request):
    """
        Handler for api route

        Executes gates method(entity) and parameters
    """

    response = await request.app["api_gate"].execute(
            entity=request.match_info['entity'],
            params=request.query)

    return aiohttp.web.json_response(response,
            dumps = lambda payload: json.dumps(payload, default=str)) 
