"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import asyncio
import socket

from notifire import constants
from notifire.exceptions import APIError, RateLimited
from notifire.transport.base import AsyncTransport
from notifire.transport.http import HTTPTransport

try:
    import aiohttp
    has_aiohttp = True
except ImportError:
    has_aiohttp = False


class AioHTTPTransportBase(AsyncTransport, HTTPTransport):
    def __init__(self, timeout=constants.TIMEOUT, verify_ssl=True,
                 keepalive=True, family=socket.AF_INET, loop=None):
        if not has_aiohttp:
            raise ImportError('AioHttpTransport requires aiohttp.')

        self._keepalive = keepalive
        self._family = family
        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop

        super().__init__(timeout, verify_ssl)

        if self.keepalive:
            self._client_session = self._client_session_factory()

        self._closing = False

    @property
    def keepalive(self):
        return self._keepalive

    @property
    def family(self):
        return self._family

    def _client_session_factory(self):
        connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl,
                                         family=self.family,
                                         loop=self._loop)
        return aiohttp.ClientSession(connector=connector,
                                     loop=self._loop)

    async def _do_send(self, url, data, headers, success_cb, failure_cb):
        if self.keepalive:
            session = self._client_session
        else:
            session = self._client_session_factory()

        resp = None

        try:
            resp = await session.post(
                url,
                data=data,
                compress=False,
                headers=headers,
                timeout=self.timeout
            )

            code = resp.status
            if not 200 <= code < 300:
                msg = await resp.text()
                if code == 429:
                    try:
                        retry_after = resp.headers.get('retry-after')
                        retry_after = int(retry_after)
                    except (ValueError, TypeError):
                        retry_after = 0
                    failure_cb(RateLimited(msg, retry_after))
                else:
                    failure_cb(APIError(msg, code))
            else:
                success_cb()
        except asyncio.CancelledError:  # pylint: disable=W0706
            # do not mute asyncio.CancelledError
            raise
        except Exception as exc:
            failure_cb(exc)
        finally:
            if resp:
                resp.release()
            if not self.keepalive:
                await session.close()

    def _async_send(self, url, data, headers, success_cb, failure_cb):
        raise NotImplementedError

    async def _close(self):
        raise NotImplementedError

    def async_send(self, url, data, headers, success_cb, failure_cb):
        if self._closing:
            failure_cb(RuntimeError(
                '{} is closed'.format(self.__class__.__name__)
            ))
            return

        self._async_send(url, data, headers, success_cb, failure_cb)

    async def _close_coro(self, timeout=None):
        try:
            await asyncio.wait_for(
                self._close(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        finally:
            if self.keepalive:
                await self._client_session.close()

    def close(self, timeout=None):
        if self._closing:
            async def dummy():
                pass

            return dummy()

        self._closing = True

        return self._close_coro(timeout=timeout)


class AioHTTPTransport(AioHTTPTransportBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tasks = set()

    def _async_send(self, url, data, headers, success_cb, failure_cb):
        coro = self._do_send(url, data, headers, success_cb, failure_cb)

        task = asyncio.ensure_future(coro, loop=self._loop)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.remove)

    async def _close(self):
        await asyncio.gather(
            *self._tasks,
            return_exceptions=True
        )

        assert len(self._tasks) == 0
