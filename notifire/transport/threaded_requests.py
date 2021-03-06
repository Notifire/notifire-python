"""
:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from notifire.transport.base import AsyncTransport
from notifire.transport.requests import RequestsHTTPTransport
from notifire.transport.threaded import AsyncWorker


class ThreadedRequestsHTTPTransport(AsyncTransport, RequestsHTTPTransport):
    def get_worker(self):
        if not hasattr(self, '_worker'):
            self._worker = AsyncWorker()
        return self._worker

    def send_sync(self, url, data, headers, success_cb, failure_cb):
        try:
            super().send(url, data, headers)
        except Exception as e:
            failure_cb(e)
        else:
            success_cb()

    def async_send(self, url, data, headers, success_cb, failure_cb):
        self.get_worker().queue(
            self.send_sync, url, data, headers, success_cb, failure_cb)
