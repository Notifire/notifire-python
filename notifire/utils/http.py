"""
:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from http import client
import socket
import ssl
import urllib.request

from notifire import constants
from notifire.utils.ssl_match_hostname import match_hostname


def urlopen(url, data=None, timeout=constants.TIMEOUT, ca_certs=None,
            verify_ssl=False, assert_hostname=None):

    class ValidHTTPSConnection(client.HTTPConnection):
        default_port = client.HTTPS_PORT

        def __init__(self, *args, **kwargs):
            client.HTTPConnection.__init__(self, *args, **kwargs)

        def connect(self):
            sock = socket.create_connection(
                address=(self.host, self.port),
                timeout=self.timeout,
            )
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()

            self.sock = ssl.wrap_socket(
                sock, ca_certs=ca_certs, cert_reqs=ssl.CERT_REQUIRED)

            if assert_hostname is not None:
                match_hostname(self.sock.getpeercert(),
                               assert_hostname or self.host)

    class ValidHTTPSHandler(urllib.request.HTTPSHandler):
        def https_open(self, req):
            return self.do_open(ValidHTTPSConnection, req)

    if verify_ssl:
        handlers = [ValidHTTPSHandler]
    else:
        try:
            handlers = [urllib.request.HTTPSHandler(
                context=ssl._create_unverified_context())]
        except AttributeError:
            handlers = []

    opener = urllib.request.build_opener(*handlers)
    return opener.open(url, data, timeout)
