"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import asyncio

import pytest

from notifire.transport.aiohttp import AioHTTPTransport


def test_loop_is_none():
    with pytest.raises(RuntimeError):
        AioHTTPTransport()


def test_explicit_loop(event_loop):
    _transport = AioHTTPTransport(loop=event_loop)

    assert _transport._loop == event_loop

    event_loop.run_until_complete(_transport.close())


def test_global_loop(event_loop):
    asyncio.set_event_loop(event_loop)

    _transport = AioHTTPTransport()

    assert _transport._loop == event_loop

    event_loop.run_until_complete(_transport.close())


def test_transport_closed_twice(event_loop, mocker):
    _transport = AioHTTPTransport(loop=event_loop)

    event_loop.run_until_complete(_transport.close())

    close_coro = mocker.spy(_transport, '_close_coro')

    event_loop.run_until_complete(_transport.close())

    assert close_coro.call_count == 0
