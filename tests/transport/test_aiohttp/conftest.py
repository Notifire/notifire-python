"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import asyncio
from functools import partial
import gc
import os

import async_timeout
from mock import patch
import pytest

from notifire.client import Client
from tests.transport.test_aiohttp.fake_server import FakeResolver, FakeServer

asyncio.set_event_loop(None)


@pytest.fixture
def event_loop(request):
    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()
    loop.set_debug(bool(os.environ.get('PYTHONASYNCIODEBUG')))
    request.addfinalizer(lambda: asyncio.set_event_loop(None))

    yield loop

    loop.call_soon(loop.stop)
    loop.run_forever()
    loop.close()

    gc.collect()


@pytest.fixture
def notifire_client(event_loop):
    transports = []

    def do_client(fake_server, cls, *args, **kwargs):
        kwargs.setdefault('loop', event_loop)

        service_api_key = 'service_api_key'
        host = patch(
            'notifire.constants.HOST', 'http://127.0.0.1:{port}'.format(
                port=fake_server.port
            )
        )
        host.start()
        client = Client(
            service_api_key,
            transport=partial(cls, *args, **kwargs)
        )

        transport = client.get_transport()
        resolver = FakeResolver(fake_server.port)
        transport._client_session._connector._resolver = resolver

        transports.append(transport)

        return client, transport

    yield do_client

    async def do_close():
        closes = [transport.close() for transport in transports]
        await asyncio.gather(*closes, loop=event_loop)

    event_loop.run_until_complete(do_close())


@pytest.fixture
def fake_server(event_loop):
    servers = []

    async def do_server(*args, **kwargs):
        kwargs.setdefault('loop', event_loop)
        server = FakeServer(*args, **kwargs)
        servers.append(server)

        await server.start()

        return server

    yield do_server

    async def do_close():
        closes = [server.close() for server in servers]
        await asyncio.gather(*closes, loop=event_loop)

    event_loop.run_until_complete(do_close())


@pytest.fixture
def wait(event_loop):
    async def do_wait(transport, timeout=1):
        coro = asyncio.gather(*transport._tasks, loop=event_loop)

        async with async_timeout.timeout(timeout, loop=event_loop):
            await coro

    return do_wait
