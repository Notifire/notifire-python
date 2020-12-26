import mock
import pytest

from notifire import client as uut
from notifire.message import Message


class TestClient:
    client = uut.Client('service_api_key')

    @mock.patch('notifire.constants.CLIENT')
    @mock.patch('notifire.dsn.datetime')
    def test_build_headers(self, time, notifire_client):
        time.utcnow().__sub__().total_seconds.return_value = '123456.789'
        notifire_client.__str__.return_value = 'notifire-python'

        assert self.client._build_headers() == {
            'Content-Type': 'application/json',
            'Content-Encoding': 'gzip',
            'X-Notifire-Auth': (
                'Notifire notifire_api_key=service_api_key, '
                'notifire_timestamp=123456.789, '
                'notifire_client={}'.format('notifire-python')
            )

        }

    @mock.patch('notifire.client.Client._send')
    @mock.patch('notifire.constants.CLIENT')
    @mock.patch('notifire.constants.PATH')
    @mock.patch('notifire.constants.HOST')
    @mock.patch('notifire.dsn.datetime')
    def test_sendNotification(self, time, host, path, notifire_client, _send):
        time.utcnow().__sub__().total_seconds.return_value = '123456.789'
        notifire_client.__str__.return_value = 'notifire-python'
        host.__str__.return_value = 'localhost'
        path.__str__.return_value = 'notify'

        self.client.send_notification(body='foo', text='bar')
        _send.assert_called_once_with(
            url='localhost/notify',
            data=Message.get_payload(body='foo', text='bar'),
            headers={
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip',
                'X-Notifire-Auth': (
                    'Notifire notifire_api_key=service_api_key, '
                    'notifire_timestamp=123456.789, '
                    'notifire_client={}'.format('notifire-python')
                )
            }
        )

        self.client.send_notification(body='foo', text='bar', sample_rate=0)
        _send.assert_called_once()

    @mock.patch('notifire.client.Client._send')
    @mock.patch('notifire.constants.CLIENT')
    @mock.patch('notifire.constants.PATH')
    @mock.patch('notifire.constants.HOST')
    @mock.patch('notifire.dsn.datetime')
    def test_send(self, time, host, path, notifire_client, _send):
        time.utcnow().__sub__().total_seconds.return_value = '123456.789'
        notifire_client.__str__.return_value = 'notifire-python'
        host.__str__.return_value = 'localhost'
        path.__str__.return_value = 'notify'

        data = Message.get_payload(body='foo', text='bar')
        self.client.send(data)

        _send.assert_called_once_with(
            url='localhost/notify',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip',
                'X-Notifire-Auth': (
                    'Notifire notifire_api_key=service_api_key, '
                    'notifire_timestamp=123456.789, '
                    'notifire_client={}'.format('notifire-python')
                )
            }
        )

        _send.side_effect = Exception()
        with pytest.raises(Exception):
            self.client.send(data)
