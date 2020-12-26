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

import mock

from notifire.client import Client
from notifire.transport import requests as uut


class TestRequestsHTTPTransport:
    client = Client('service_api_key', transport=uut.RequestsHTTPTransport)

    @mock.patch('notifire.transport.requests.requests.post')
    @mock.patch('notifire.constants.PATH')
    @mock.patch('notifire.constants.HOST')
    def test_does_send(self, host, path, post):
        host.__str__.return_value = 'localhost'
        path.__str__.return_value = 'notify'
        self.client.send_notification('foo')
        assert post.call_count == 1
        expected_url = 'localhost/notify'
        assert expected_url == post.call_args[0][0]
