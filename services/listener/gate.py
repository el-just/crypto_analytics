# -*- coding: utf-8 -*-
"""
The main gate to route api requests

Aggregatest api logic
"""

from importlib import import_module

class Gate:
    async def execute(self, entity, params):
        """
            Main entry point. Responsible for passing parameters and other
        """

        return await getattr(self, entity)(**params)

    async def ping(self):
        """
            Basic answer, to know that service is up
        """

        return {'status': 'ready'}

