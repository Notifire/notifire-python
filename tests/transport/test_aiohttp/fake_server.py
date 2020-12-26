"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import asyncio
from collections import defaultdict
import socket

from aiohttp import web
from aiohttp.test_utils import unused_port


class FakeResolver:
    _LOCAL_HOST = {
        0: '127.0.0.1',
        socket.AF_INET: '127.0.0.1',
        socket.AF_INET6: '::1',
    }

    def __init__(self, port):
        self.port = port

    async def resolve(self, host, port=0, family=socket.AF_INET):
        return [
            {
                'hostname': host,
                'host': self._LOCAL_HOST[family],
                'port': self.port,
                'family': family,
                'proto': 0,
                'flags': socket.AI_NUMERICHOST,
            },
        ]


class FakeServer:

    app = None
    runner = None
    site = None

    host = '127.0.0.1'

    def __init__(self, loop, side_effect=None):
        self.loop = loop

        if not side_effect:
            side_effect = {
                'status': 200,
            }

        self._side_effect = side_effect
        self._slop_factor = 0

        self.app = web.Application()
        self.setup_routes()

        self.port = unused_port()

        self.hits = defaultdict(lambda: 0)

    @property
    def side_effect(self):
        return self._side_effect

    @property
    def slop_factor(self):
        return self._slop_factor

    @slop_factor.setter
    def slop_factor(self, value):
        self._slop_factor = value

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

    def setup_routes(self):
        self.app.router.add_post('/notify', self.notify)

    async def notify(self, request):
        await asyncio.sleep(self.slop_factor, loop=self.loop)

        self.hits[self.side_effect['status']] += 1
        return web.Response(**self.side_effect)

    async def close(self):
        if self.runner:
            await self.runner.cleanup()
