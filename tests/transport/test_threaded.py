"""
:copyright: (c) 2010-2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import os
from tempfile import mkstemp
import time

import mock

from notifire.client import Client
from notifire.message import Message
from notifire.transport import threaded as uut


class DummyThreadedScheme(uut.ThreadedHTTPTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
        self.send_delay = 0

    def send_sync(self, url, data, headers, success_cb, failure_cb):
        # delay sending the message, to allow us to tests that the shutdown
        # hook waits correctly
        time.sleep(self.send_delay)

        self.events.append((url, data, headers, success_cb, failure_cb))


class LoggingThreadedScheme(uut.ThreadedHTTPTransport):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def send_sync(self, url, data, headers, success_cb, failure_cb):
        with open(self.filename, 'a') as log:
            log.write(
                '{0} {1}\n'.format(
                    os.getpid(),
                    data['message']['titleBody'])
            )


class TestThreadedHTTPTransport:
    url = 'localhost'
    message = Message()
    client = Client('service_api_key', transport=uut.ThreadedHTTPTransport)

    @mock.patch('notifire.transport.http.HTTPTransport.send')
    def test_does_send(self, send):
        self.client.send_notification('foo', level='info')

        time.sleep(0.1)

        assert send.call_count == 1

    def test_shutdown_waits_for_send(self):
        transport = DummyThreadedScheme()
        transport.send_delay = 0.5

        data = self.message.get_payload(
            'foo',
            level='info',
            text=None,
            url=None
        )
        transport.async_send(self.url, data, None, None, None)

        time.sleep(0.1)

        # this should wait for the message to be sent
        transport.get_worker().main_thread_terminated()

        assert len(transport.events) == 1

    def test_fork_spawns_anew(self):
        transport = DummyThreadedScheme()
        transport.send_delay = 0.5

        data = self.message.get_payload(
            'foo',
            level='info',
            text=None,
            url=None
        )

        pid = os.fork()
        if pid == 0:
            time.sleep(0.1)

            transport.async_send(self.url, data, None, None, None)

            # this should wait for the message to get sent
            transport.get_worker().main_thread_terminated()

            assert len(transport.events) == 1
            # Use os._exit here so that pytest will not get confused about
            # what the hell we're doing here.
            os._exit(0)
        else:
            os.waitpid(pid, 0)

    def test_fork_with_active_worker(self):
        """
        Test threaded transport when forking an active worker.
        Forking a process doesn't clone the worker thread - make sure
        logging from both processes still works.
        """
        event1 = self.message.payload(
            'parent',
            level='info',
            text=None,
            url=None
        )
        event2 = self.message.payload(
            'child',
            level='info',
            text=None,
            url=None
        )
        fd, filename = mkstemp()
        try:
            os.close(fd)
            transport = LoggingThreadedScheme(filename)

            # Log from the parent process - starts the worker thread
            transport.async_send(self.url, event1, None, None, None)
            childpid = os.fork()

            if childpid == 0:
                # Log from child process
                transport.async_send(self.url, event2, None, None, None)

                # Ensure threaded worker has finished
                transport.get_worker().stop()
                os._exit(0)

            # Wait for the child process to finish
            os.waitpid(childpid, 0)
            assert os.path.isfile(filename)

            # Ensure threaded worker has finished
            transport.get_worker().stop()

            with open(filename, 'r') as logfile:
                events = dict(x.strip().split() for x in logfile.readlines())

            # Check that parent and child both logged successfully
            assert events == {
                str(os.getpid()): 'parent',
                str(childpid): 'child'
            }
        finally:
            os.remove(filename)
