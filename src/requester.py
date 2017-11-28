import requests

from .mingle_auth import MingleAuth


class Requester:
    def __init__(self, host, project, user_name, secret_key):
        self.my_auth = MingleAuth(user_name, secret_key)
        self.my_host = host
        self.my_project = project

    def get_events(self):
        response = requests.get(
            self.my_host + '/api/v2/projects/' + self.my_project + '/feeds/events.xml',
            auth=self.my_auth)
        return response.content
