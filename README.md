# Notifire - Python client for [Notifire](https://notifire.dvdblk.com)

[![Build Status](https://travis-ci.org/Notifire/Notifire-python.svg?branch=master)](https://travis-ci.org/github/Notifire/Notifire-python)
[![PyPi page link -- version](https://img.shields.io/pypi/v/notifire.svg)](https://pypi.org/project/notifire)

Notifire-Python is Python client used for sending Apple push notifications from your code to your iOS device with
the Notifire application.
Notification is sent as a HTTP request to the Notifire server through various implemented transports.

### Usage
Notifire has an account management system. This allows you to preserve your data across various iOS devices.
You can either create Notifire account or use 3rd party accounts (e.g. Google).<br/>
Create a service in the Notifire iOS application.
Then you obtain **service api key** that you can either pass directly to the client class or through the environment
variable `NOTIFIRE_SERVICE_API_KEY`.

Install notifire with pip:
```
pip install notifire
```
Create and configure a client:
```python
from notifire import Client

client = Client('service_api_key')
client.send_notification('Hello from Python')
```

### Notification
The notification consists of
 - body (required) - title of the iOS notification pop-up
 - level - one of `info`/`error`/`warning` to filter the notification
 - text - additional text of the notification shown in notification tab
 - url - url displayed in the notification

These parameters are accepted by`send_notification` method.
Notifications are aggregated under a *service* which you create in the Notifire iOS application.<br/>
Service is a representation of your code/script/application from which you send these notifications.

### Transports
A transport is the mechanism through which Notifire sends the HTTP request to the Notifire server.
There are 6 types of transports implemented:
 - AioHttpTransport - should be used in asyncio based environments
 - GeventedHTTPTransport - should be used in gevent based environments
 - HTTPTransport - synchronous blocking transport, can be used in any environment
 - RequestsHTTPTransport - synchronous blocking transport using `requests` library, can be used in any environment
 - ThreadedHTTPTransport (Default) - spawns a thread (async worker) that is processing messages
 - ThreadedRequestsHTTPTransport - spawns a thread (async worker) that is using `requests` library for processing messages

To use your desired transport, simply import and pass it to the Client class.
```python
from notifire import Client
from notifire.transport import ThreadedHTTPTransport

client = Client('service_api_key', transport=ThreadedHTTPTransport)
```

#### Integrations
You can use Notifire with the legacy Sentry python client [Raven](https://github.com/getsentry/raven-python).
This will allow you to receive errors to Notifire as well as to Sentry.

Install notifire and raven from pip:
```
pip install notifire[raven]
```
Create and configure a client which serves as both Notifire and Sentry client:
```python
from notifire.integrations.raven import Client

client = Client(service_api_key='service_api_key',
                sentry_dsn='__DSN__')
```
