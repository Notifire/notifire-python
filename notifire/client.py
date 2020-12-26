import logging
import os
from random import Random

from notifire.dsn import Dsn
from notifire.exceptions import APIError
from notifire.message import Message
from notifire.transport.threaded import ThreadedHTTPTransport

log = logging.getLogger('notifire')


class Client:
    """Client for sending notifications to Notifire via configured transport.

    >>> from notifire import Client

    >>> # Read service api key configuration from
    >>> # ``os.environ['NOTIFIRE_SERVICE_API_KEY']``
    >>> client = Client()

    >>> # or pass service api key to the client
    >>> client = Client(service_api_key='service_api_key')

    >>> # Send message
    >>> client.send_notification('Hello from Python')
    """

    def __init__(
        self,
        service_api_key=None,
        transport=None,
        raise_send_errors=False,
        _random_seed=None,
        **options
    ):
        service_api_key = os.environ.get('NOTIFIRE_SERVICE_API_KEY',
                                         service_api_key)
        self.dsn = Dsn(service_api_key)
        self._transport = transport or ThreadedHTTPTransport
        self._random = Random(_random_seed)
        self.raise_send_errors = raise_send_errors
        self.sample_rate = options.get('sample_rate', 1)
        self.success_callback = options.get('success_callback',
                                            self.successful_send)

    def get_transport(self):
        """Instantiate transport class outside of init.

        This prevents creation of loop or spawning new thread too
        early. Also ensuring that only one instance of transport class
        will be present.
        """
        if not hasattr(self, 'transport'):
            self.transport = self._transport()
        return self.transport

    def send_notification(self, body, level='info', text=None, url=None,
                          sample_rate=None):
        """Capture and send message to notifire application.

        :param body: str, the title of the iOS notification pop-up
        :param level: str, one of ('info', 'warning', 'error')
                      to filter the notification
        :param text: str, additional text of the notification
                     shown in notification tab
        :param url: str, url displayed in the notification
        :param sample_rate: float, in the range of [0, 1], process rate
                            of this event
        :return:
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if self._random.random() >= sample_rate:
            return

        data = Message.get_payload(body, level, text, url)
        self.send(data)

    def _build_headers(self):
        return {
            'X-Notifire-Auth': self.dsn.auth_header(),
            'Content-Type': 'application/json',
            'Content-Encoding': 'gzip'
        }

    def send(self, data):
        return self._send(
            url=self.dsn.api_url,
            data=data,
            headers=self._build_headers()
        )

    def _send(self, url, data, headers):
        def failed_send(e):
            self._failed_send(e, url, Message.decode(data))

        try:
            transport = self.get_transport()
            if transport.is_async:
                transport.async_send(url, data, headers, self.successful_send,
                                     failed_send)
            else:
                transport.send(url, data, headers)
        except Exception as e:
            if self.raise_send_errors:
                raise
            failed_send(e)

    @staticmethod
    def _failed_send(exc, url, data):
        if isinstance(exc, APIError):
            log.error('Notifire api responded with an error: %s(%s)',
                      type(exc).__name__, exc.message)

        else:
            log.error('Notifire api responded with an error: %s (url: %s)',
                      exc, url, exc_info=True, extra={'data': data})

    @staticmethod
    def successful_send():
        """Callback for successful message delivery."""
        return
