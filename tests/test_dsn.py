import mock

from notifire import constants
from notifire import dsn as uut


class TestDsn:
    service_api_key = 'service_api_key'
    dsn = uut.Dsn(service_api_key)

    def test_init(self):
        assert self.dsn.service_api_key == self.service_api_key

    @mock.patch('notifire.constants.PATH')
    @mock.patch('notifire.constants.HOST')
    def test_api_url(self, host, path):
        host.__str__.return_value = 'localhost'
        path.__str__.return_value = 'notify'

        assert self.dsn.api_url == 'localhost/notify'

    def test_auth_header(self):
        with mock.patch('notifire.dsn.datetime') as time:
            time.utcnow().__sub__().total_seconds.return_value = '123456.789'
            assert self.dsn.auth_header() == (
                'Notifire notifire_service_api_key={0}, '
                'notifire_timestamp={1}, '
                'notifire_client={2}'
                .format(self.service_api_key, '123456.789', constants.CLIENT)
            )
