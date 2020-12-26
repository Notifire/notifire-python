import argparse

from notifire.client import Client
from notifire.transport import HTTPTransport


def main():
    parser = argparse.ArgumentParser(
        prog='notifire',
        description='cli for notifire client library')
    parser.add_argument(
        '-s',
        '--service_api_key',
        required=True,
        help='service api key')
    parser.add_argument(
        '-b',
        '--body',
        required=True,
        help='the title of the iOS notification pop-up')
    parser.add_argument(
        '-l',
        '--level',
        default='info',
        help="one of ('info', 'warning', 'error') to filter the notification")
    parser.add_argument(
        '-t',
        '--text',
        help='additional text of the notification shown in notification tab')
    parser.add_argument(
        '-u',
        '--url',
        help='url displayed in the notification')
    args = vars(parser.parse_args())
    service_api_key = args.pop('service_api_key')
    Client(service_api_key, transport=HTTPTransport).send_notification(**args)
