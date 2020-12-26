"""
:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import urllib.request

import certifi

from notifire import constants
from notifire.exceptions import APIError, RateLimited
from notifire.transport.base import Transport
from notifire.utils.http import urlopen


class HTTPTransport(Transport):
    """The default HTTP transport."""

    def __init__(self, timeout=constants.TIMEOUT, verify_ssl=True,
                 ca_certs=None):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.ca_certs = ca_certs or certifi.where()

    def send(self, url, data, headers):
        """Send request to a remote webserver using HTTP POST."""

        req = urllib.request.Request(url, headers=headers)

        try:
            response = urlopen(
                url=req,
                data=data,
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
                ca_certs=self.ca_certs,
            )
        except urllib.request.HTTPError as exc:
            msg = exc.headers.get('x-notifire-error')
            code = exc.getcode()
            if code == 429:  # pylint: disable=R1720
                try:
                    retry_after = int(exc.headers.get('retry-after'))
                except (ValueError, TypeError):
                    retry_after = 0
                raise RateLimited(msg, retry_after) from exc
            elif msg:
                raise APIError(msg, code) from exc
            else:
                raise
        return response
