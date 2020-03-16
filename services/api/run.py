# -*- coding: utf-8 -*-
"""
Api service Runner

Main file of service
"""

import os
import sys
import platform
import socket
import asyncio
import uvloop

from aiohttp import web

import entry_points
from gate import Gate

class Runner:
    __loop = None

    def __init__(self, loop):
        self.__loop = loop
        self.__setup_path()

    async def run(self):
        """
            Setting up Gate, routes and main socket
        """

        app = web.Application()
        app["api_gate"] = Gate()

        app.add_routes([
            web.get('/api/v1/{entity}', entry_points.api),
            ])

        runner = web.AppRunner(app)
        await runner.setup()

        sock = self.__make_socket()
        srv = web.SockSite(runner, sock)
        await srv.start()

        return srv, app, runner

    async def finalize(self, srv, app):
        """
            Close socket on Interrupt
        """

        if hasattr(srv, 'sockets'):
            sock = srv.sockets[0]
            app.loop.remove_reader(sock.fileno())
            sock.close()

        srv.close()
        await srv.wait_closed()
        await app.finish()

    def __make_socket(self, host="0.0.0.0", port=6543, reuseport=False):
        """
            Socket creation
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if reuseport:
            SO_REUSEPORT = 15
            sock.setsockopt(socket.SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind((host, port))
        return sock

    def __setup_path(self):
        """
            setting up path for ca_common modules
        """

        delimiter = '/' if platform.system() == 'Linux' else '\\'
        common_path = delimiter.join(
                os.path.dirname(os.path.abspath(__file__)).split(delimiter)[:-1])
        sys.path.append(common_path)


if __name__ == '__main__':
    """
        Running EventLoop
    """

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = Runner(loop)

    srv, app, handler = loop.run_until_complete(runner.run())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete((runner.finalize(srv, app, handler)))
