try:
    from raven import Client as SentryClient
except ImportError:
    import pytest
    pytest.skip(
        'Testing raven transport requires raven.',
        allow_module_level=True
    )

import mock

from notifire import Client as NotifireClient
from notifire.integrations import raven as uut
from notifire.transport.base import AsyncTransport


class TestClient:
    service_api_key = 'service_api_key'
    sentry_dsn = 'https://public_key:secret_key@sentry.local/project_id'
    client = uut.Client(
        service_api_key=service_api_key,
        sentry_dsn=sentry_dsn
    )

    def test_init(self):
        assert isinstance(self.client, SentryClient)
        assert isinstance(self.client.notifire_client, NotifireClient)

    @staticmethod
    @mock.patch('raven.conf.remote.RemoteConfig.get_transport')
    def test_shared_transport(get_transport):
        transport = mock.Mock(spec=AsyncTransport)
        get_transport.return_value = transport
        # not using already created client instance because of patching
        # that affects init
        service_api_key = 'service_api_key'
        sentry_dsn = 'https://public_key:secret_key@sentry.local/project_id'
        client = uut.Client(
            service_api_key=service_api_key,
            sentry_dsn=sentry_dsn
        )

        try:
            1 / 0
        except ZeroDivisionError:
            client.captureException()

        # request should be sent over the same transport instance
        assert transport.async_send.call_count == 2
        client.send_notification(body='foo', text='bar')
        assert transport.async_send.call_count == 3

    @mock.patch('raven.base.Client.send')
    @mock.patch('raven.base.Client.build_msg')
    @mock.patch('notifire.client.Client.send_notification')
    def test_send(self, sendNotification, build_msg, send):
        data = {
            'level': 40,
            'message': 'ZeroDivisionError: division by zero',
            'event_id': '1337'
        }
        build_msg.return_value = data

        try:
            1 / 0
        except ZeroDivisionError:
            self.client.captureException()

        send.assert_called_once_with(None, **data)
        sendNotification.assert_called_once_with(
            data['message'],
            'error',
            None, None, None
        )

    @mock.patch('raven.base.Client.send_remote')
    @mock.patch('notifire.client.Client.send_notification')
    def test_sendNotification(self, sendNotification, send_remote):
        self.client.send_notification(body='foo', text='bar')
        send_remote.assert_not_called()
        sendNotification.assert_called_once_with(
            'foo',
            'info',
            'bar',
            None,
            None
        )
