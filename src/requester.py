import os
from urllib.parse import urlparse

import requests

from .mingle_auth import MingleAuth


class Requester:
    def __init__(self, host, project, user_name, secret_key):
        self.my_auth = MingleAuth(user_name, secret_key)
        self.my_host = host
        self.my_project = project

    def get_events(self, url=None):
        if not os.path.exists('result/caches'):
            os.makedirs('result/caches')
        if url:
            query = urlparse(url).query
            xml = 'result/caches/events-' + self.my_project + '-' + query + '.xml'
            if os.path.exists(xml):
                with open(xml, 'r') as f:
                    cache_xml = f.read()
                return cache_xml
            response = requests.get(
                url, auth=self.my_auth)
            with open(xml, 'w') as f:
                f.write(response.content.decode())
        else:
            response = requests.get(
                self.my_host + '/api/v2/projects/' + self.my_project + '/feeds/events.xml',
                auth=self.my_auth)
        return response.content

    def get_cards_by_mql(self, mql):
        json_body = '{"mql":"' + mql + '"}'
        response = requests.request(
            method='GET',
            url=self.my_host + '/api/v2/projects/' + self.my_project + '/cards/execute_mql.xml',
            auth=self.my_auth,
            data=json_body)
        return response.content

    def get_card_version(self, number, version):
        json_body = '{"version":"' + version + '"}'
        response = requests.request(
            method='GET',
            url=self.my_host + '/api/v2/projects/' + self.my_project + '/cards/' + number + '.xml',
            auth=self.my_auth,
            data=json_body)
        return response.content
