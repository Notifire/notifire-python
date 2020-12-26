import pytest

from notifire.client import Client
from notifire.transport import base as uut


class TestTransport:
    client = Client('service_api_key', transport=uut.Transport,
                    raise_send_errors=True)

    def test_send(self):
        with pytest.raises(NotImplementedError):
            self.client.send_notification('foo')


class TestAsyncTransport:
    client = Client('service_api_key', transport=uut.AsyncTransport,
                    raise_send_errors=True)

    def test_async_send(self):
        with pytest.raises(NotImplementedError):
            self.client.send_notification('foo')
