import gzip
import io
import json
import sys

from notifire import constants
from notifire.exceptions import InvalidNotificationLevel, MessageSizeExceeded


class Message:
    levels = ('info', 'warning', 'error')

    @classmethod
    def get_payload(cls, body, level='info', text=None, url=None):
        if level.lower() not in cls.levels:
            raise InvalidNotificationLevel(
                'Notification level must be one of {}'
                .format(cls.levels))
        payload = cls.payload(body, level, text, url)
        payload = json.dumps(payload).encode('utf-8')

        if not cls.check_size(payload):
            raise MessageSizeExceeded(
                'Size of a message exceeded maximum of {} bytes'
                .format(constants.MESSAGE_SIZE))

        return cls.encode(payload)

    @staticmethod
    def payload(body, level, text, url):
        return {
            'level': level,
            'message': {
                'titleBody': body,
                'text': text,
                'url': url
            }
        }

    @staticmethod
    def encode(data):
        body = io.BytesIO()
        with gzip.GzipFile(fileobj=body, mode='w') as f:
            f.write(data)
        return body.getvalue()

    @staticmethod
    def decode(data):
        return gzip.GzipFile(fileobj=io.BytesIO(data)).read()

    @staticmethod
    def check_size(payload):
        return sys.getsizeof(payload) < constants.MESSAGE_SIZE
