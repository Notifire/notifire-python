from datetime import datetime

from notifire import constants

EPOCH = datetime(1970, 1, 1)


class Dsn:
    def __init__(self, service_api_key):
        self.service_api_key = service_api_key

    @property
    def api_url(self):
        return '{host}/{path}'.format(
            host=constants.HOST,
            path=constants.PATH
        )

    def auth_header(self):
        header = [
            ('notifire_service_api_key', self.service_api_key),
            ('notifire_timestamp', (datetime.utcnow() - EPOCH)
             .total_seconds()),
            ('notifire_client', constants.CLIENT)
        ]
        return 'Notifire ' + ', '.join('{}={}'.format(key, value)
                                       for key, value in header)
