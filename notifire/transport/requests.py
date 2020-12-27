"""
:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from notifire.exceptions import APIError, RateLimited
from notifire.transport.http import HTTPTransport

try:
    import requests
    has_requests = True
except ImportError:
    has_requests = False


class RequestsHTTPTransport(HTTPTransport):
    def __init__(self, *args, **kwargs):
        if not has_requests:
            raise ImportError('RequestsHTTPTransport requires requests.')

        super().__init__(*args, **kwargs)

    def send(self, url, data, headers):
        if self.verify_ssl:
            # If SSL verification is enabled, use the provided CA bundle to
            # perform the verification
            self.verify_ssl = self.ca_certs
        try:
            resp = requests.post(url, data=data, headers=headers,
                                 verify=self.verify_ssl, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            msg = exc.response.text
            code = exc.response.status_code
            print(exc.response.headers.get('retry-after'))
            if code == 429:  # pylint: disable=R1720
                try:
                    retry_after = exc.response.headers.get('retry-after')
                    retry_after = int(retry_after)
                except (ValueError, TypeError):
                    retry_after = 0
                raise RateLimited(msg, retry_after) from exc
            elif msg:
                raise APIError(msg, code) from exc
            else:
                raise
