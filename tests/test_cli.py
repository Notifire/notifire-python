import mock
import pytest

from notifire import cli as uut


@mock.patch('notifire.client.Client.send_notification')
def test_main(client):
    kwargs = {
        'body': 'foo',
        'level': 'error',
        'text': 'bar',
        'url': 'https://notifire.notifire'
    }
    with mock.patch(
        'argparse._sys.argv', [
            'notifire-cli',
            '--service_api_key',
            'service_api_key',
            '--body',
            kwargs['body'],
            '--level',
            kwargs['level'],
            '--text',
            kwargs['text'],
            '--url',
            kwargs['url']
        ]
    ):
        uut.main()
    client.assert_called_with(**kwargs)

    with mock.patch(
        'argparse._sys.argv', [
            'notifire-cli',
            '--service_api',
            'service_api_key',
            '--body',
            kwargs['body'],
            '--random_arg',
            'this should trigger error'
        ]
    ):
        with pytest.raises(SystemExit):
            uut.main()
