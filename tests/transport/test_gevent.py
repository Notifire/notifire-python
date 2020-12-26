"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

try:
    from gevent import monkey; monkey.patch_all()  # NOQA
except ImportError:
    import pytest
    pytest.skip(
        'Testing gevent transport requires gevent.',
        allow_module_level=True
    )

import time

import mock

from notifire.client import Client
from notifire.transport import gevent as uut


class TestGeventedHTTPTransport:
    client = Client('service_api_key', transport=uut.GeventedHTTPTransport)

    @mock.patch.object(uut.GeventedHTTPTransport, '_done')
    @mock.patch('notifire.transport.http.HTTPTransport.send')
    def test_does_send(self, send, done):
        self.client.send_notification('foo')
        time.sleep(0)
        assert send.call_count == 1
        time.sleep(0)
        assert done.call_count == 1
