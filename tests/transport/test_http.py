import mock

from notifire.client import Client
from notifire.transport import http as uut


class TestRequestsHTTPTransport:
    client = Client('service_api_key', transport=uut.HTTPTransport)

    @mock.patch('urllib.request.OpenerDirector.open')
    def test_does_send(self, request):
        self.client.send_notification('foo')
        assert request.call_count == 1
