"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import asyncio
import logging

import mock
import pytest

from notifire.transport.aiohttp import AioHTTPTransport
from tests.transport.test_aiohttp.utils import Logger

pytestmark = pytest.mark.asyncio


async def test_basic(fake_server, notifire_client, wait):
    server = await fake_server()

    client, transport = notifire_client(server, AioHTTPTransport)

    client.send_notification('foo', level='info')

    await wait(transport)

    assert server.hits[200] == 1


async def test_no_keepalive(fake_server, notifire_client, wait):
    transport = AioHTTPTransport(keepalive=False)
    assert not hasattr(transport, '_client_session')
    await transport.close()

    server = await fake_server()

    client, transport = notifire_client(server, AioHTTPTransport)
    transport._keepalive = False
    session = transport._client_session

    def _client_session_factory():
        return session

    with mock.patch(
        'notifire.transport.aiohttp.AioHTTPTransport._client_session_factory',
        side_effect=_client_session_factory,
    ):
        client.send_notification('foo', level='info')

        await wait(transport)

        assert session.closed

        assert server.hits[200] == 1


async def test_close_timeout(fake_server, notifire_client):
    server = await fake_server()
    server.slop_factor = 100

    client, transport = notifire_client(server, AioHTTPTransport)

    client.send_notification('foo', level='info')

    await transport.close(timeout=0)

    assert server.hits[200] == 0


async def test_rate_limit(fake_server, notifire_client, wait):
    server = await fake_server()
    server.side_effect['status'] = 429

    with Logger('notifire', level=logging.ERROR) as log:
        client, transport = notifire_client(server, AioHTTPTransport)

        client.send_notification('foo', level='error')

        await wait(transport)

        assert server.hits[429] == 1

    msg = 'Notifire api responded with an error: RateLimited(None)'
    assert log.msgs[0] == msg


async def test_status_500(fake_server, notifire_client, wait):
    server = await fake_server()
    server.side_effect['status'] = 500

    with Logger('notifire', level=logging.ERROR) as log:
        client, transport = notifire_client(server, AioHTTPTransport)

        client.send_notification('foo', level='error')

        await wait(transport)

        assert server.hits[500] == 1

    msg = 'Notifire api responded with an error: APIError(None)'
    assert log.msgs[0] == msg


async def test_cancelled_error(fake_server, notifire_client, wait):
    server = await fake_server()

    with mock.patch('aiohttp.ClientSession.post',
                    side_effect=asyncio.CancelledError):
        client, transport = notifire_client(server, AioHTTPTransport)

        client.send_notification('foo', level='error')

        with pytest.raises(asyncio.CancelledError):
            await wait(transport)

        assert server.hits[200] == 0


async def test_async_send_when_closed(fake_server, notifire_client):
    server = await fake_server()

    with Logger('notifire', level=logging.ERROR) as log:
        client, transport = notifire_client(server, AioHTTPTransport)

        close = transport.close()

        client.send_notification('foo', level='error')

        assert server.hits[200] == 0

    assert log.msgs[0].startswith(
        'Notifire api responded with an error: AioHTTPTransport is closed')

    await close
