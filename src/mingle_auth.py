import base64
import datetime
import hmac
from hashlib import sha1
from urllib.parse import urlparse


class MingleAuth:
    def __init__(self, user_name, secret_key):
        self.user_name = user_name
        self.secret_key = secret_key

    def __call__(self, request):
        path = urlparse(request.url).path
        query = urlparse(request.url).query
        if query:
            path += '?' + query
        timestamp = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S UTC')
        if request.body:
            request.headers['content-type'] = 'application/json'
            canonical_string = 'application/json,,' + path + ',' + timestamp
        else:
            canonical_string = ',,' + path + ',' + timestamp
        digest = hmac.new(self.secret_key.encode('utf-8'), canonical_string.encode('utf-8'), sha1).digest()
        auth_string = base64.b64encode(digest).decode()

        request.headers['authorization'] = 'APIAuth ' + self.user_name + ':' + auth_string
        request.headers['date'] = timestamp
        return request
