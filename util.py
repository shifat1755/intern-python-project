import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from time import sleep, time

class NetworkRequest:
    baseApi = 'http://127.0.0.1:8000'

    @staticmethod
    def get(url, headers={}):
        req = Request(url=NetworkRequest.baseApi + url, method='GET')
        for key, value in headers.items():
            req.add_header(key, value)
        try:
            with urlopen(req) as res:
                body = res.read().decode('utf-8')
                return {'body': json.loads(body), 'code': res.status}
        except HTTPError as e:
            return {'error': e.reason, 'code': e.code}

    @staticmethod
    def post(url, payload={}, headers={}):
        req = Request(url=NetworkRequest.baseApi + url, method='POST')
        for key, value in headers.items():
            req.add_header(key, value)
        req.add_header('Content-Type', 'application/json')
        try:
            with urlopen(req, data=json.dumps(payload).encode('utf-8')) as res:
                body = res.read().decode('utf-8')
                return {'body': json.loads(body), 'code': res.status}
        except HTTPError as e:
            return {'error': e.reason, 'code': e.code}

    @staticmethod
    def put(url, payload={}, headers={}):
        req = Request(url=NetworkRequest.baseApi + url, method='PUT')
        for key, value in headers.items():
            req.add_header(key, value)
        req.add_header('Content-Type', 'application/json')
        try:
            with urlopen(req, data=json.dumps(payload).encode('utf-8')) as res:
                body = res.read().decode('utf-8')
                return {'body': json.loads(body), 'code': res.status}
        except HTTPError as e:
            return {'error': e.reason, 'code': e.code}

    @staticmethod
    def delete(url, headers={}):
        req = Request(url=NetworkRequest.baseApi + url, method='DELETE')
        for key, value in headers.items():
            req.add_header(key, value)
        try:
            with urlopen(req) as res:
                body = res.read().decode('utf-8')
                return {'body': json.loads(body), 'code': res.status}
        except HTTPError as e:
            return {'error': e.reason, 'code': e.code}

def retry_with_token_refresh(func):
    def wrapper(*args, **kwargs):
        refresh_token = kwargs.pop('refresh_token', None)
        result = func(*args, **kwargs)
        if result.get('code') == 401 and refresh_token:
            print("requesting new access token..")
            refresh_response = NetworkRequest.post('/api/auth/token', {'refresh_token': refresh_token})
            if refresh_response.get('code') == 200:
                print("got new token..\n")
                new_token = refresh_response['body']['access_token']
                kwargs['headers']['Authorization'] = f'Bearer {new_token}'
                return func(*args, **kwargs)
        return result
    return wrapper
