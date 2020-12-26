from raven import Client as SentryClient

from notifire import Client as NotifireClient

LEVELS = {
    'critical': 'error',
    'fatal': 'error',
    'error': 'error',
    'warning': 'warning',
    'warn': 'warning',
    'info': 'info',
    'debug': 'info',
    'notset': 'info',
    50: 'error',
    40: 'error',
    30: 'warning',
    20: 'info',
    10: 'info',
    0: 'info'
}


class Client(SentryClient):
    """Client for sending notifications to Notifire via configured transport.

    Client also works independently as Sentry client
    and all of its data can be forwarded as a notification to Notifire.

    >>> from notifire import Client

    >>> # Read configuration from
    >>> # ``os.environ['NOTIFIRE_SERVICE_API_KEY']``,
    >>> # ``os.environ['SENTRY_DSN']``
    >>> client = Client()

    >>> # or pass dsn to the client
    >>> client = Client(
    >>>     service_api_key='service_api_key',
    >>>     sentry_dsn='https://public_key:secret_key@sentry.local/project_id'
    >>> )

    >>> # Send message
    >>> client.send_notification('Hello from python')

    >>> # Record an exception
    >>> try:
    >>>     1/0
    >>> except ZeroDivisionError:
    >>>     ident = client.get_ident(client.captureException())
    >>>     print "Exception caught; reference is %s" % ident
    """

    def __init__(
        self,
        service_api_key=None,
        sentry_dsn=None,
        raise_send_errors=False,
        transport=None,
        install_sys_hook=True,
        install_logging_hook=True,
        hook_libraries=None,
        enable_breadcrumbs=True,
        _random_seed=None,
        **options
    ):
        super().__init__(
            sentry_dsn,
            raise_send_errors,
            transport,
            install_sys_hook,
            install_logging_hook,
            hook_libraries,
            enable_breadcrumbs,
            _random_seed,
            **options
        )
        self.notifire_client = NotifireClient(
            service_api_key,
            raise_send_errors=raise_send_errors,
            _random_seed=_random_seed,
            **options
        )
        self.notifire_client.get_transport = self.remote.get_transport

    def send(
        self,
        auth_header=None,
        **data
    ):
        super().send(auth_header, **data)
        level = data.get('level', 'info')
        if isinstance(level, str):
            level = level.lower()
        self.send_notification(body=data['message'], level=LEVELS[level])

    def send_notification(
        self,
        body,
        level='info',
        text=None,
        url=None,
        sample_rate=None
    ):
        self.notifire_client.send_notification(
            body,
            level,
            text,
            url,
            sample_rate
        )
