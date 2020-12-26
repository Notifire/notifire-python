"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

try:
    import requests  # NOQA, pylint: disable=W0611
except ImportError:
    import pytest
    pytest.skip(
        'Testing requests transport requires requests.',
        allow_module_level=True
    )

import time

import mock

from notifire.client import Client
from notifire.message import Message
from notifire.transport import threaded_requests as uut


class DummyThreadedScheme(uut.ThreadedRequestsHTTPTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
        self.send_delay = 0

    def send_sync(self, url, data, headers, success_cb, failure_cb):
        # delay sending the message, to allow us to tests that the shutdown
        # hook waits correctly
        time.sleep(self.send_delay)

        self.events.append((url, data, headers, success_cb, failure_cb))


class TestThreadedRequestsHTTPTransport:
    message = Message()
    client = Client(
        'service_api_key',
        transport=uut.ThreadedRequestsHTTPTransport
    )

    @mock.patch('notifire.transport.requests.requests.post')
    @mock.patch('notifire.constants.PATH')
    @mock.patch('notifire.constants.HOST')
    def test_does_send(self, host, path, send):
        host.__str__.return_value = 'localhost'
        path.__str__.return_value = 'notify'
        self.client.send_notification('foo')

        time.sleep(0.1)

        assert send.call_count == 1
        expected_url = 'localhost/notify'
        assert expected_url == send.call_args[0][0]

    def test_shutdown_waits_for_send(self):
        transport = DummyThreadedScheme()
        transport.send_delay = 0.5

        data = self.message.get_payload(
            'foo',
            level='info',
            text=None,
            url=None
        )
        transport.async_send('localhost', data, None, None, None)

        time.sleep(0.1)

        # this should wait for the message to get sent
        transport.get_worker().main_thread_terminated()

        assert len(transport.events) == 1
