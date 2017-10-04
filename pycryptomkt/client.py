import hashlib
import hmac

import requests
import time

from functools import reduce


class CryptoMKT(object):

    BASE_URL = 'https://api.cryptomkt.com'
    API_VERSION = 'v1'
    ENDPOINT_BALANCE = 'balance'
    ENDPOINT_BOOK = 'book'
    ENDPOINT_MARKETS = 'market'
    ENDPOINT_TICKER = 'ticker'
    ENDPOINT_TRADES = 'trades'

    def __init__(self, api_key=None, api_secret=None):

        self.api_key = api_key
        self.api_secret = api_secret

    def check_has_tokens(self):

        if self.api_key is None:
            raise InvalidTokensException('API Key is required')
        if self.api_secret is None:
            raise InvalidTokensException('API Secret is required')

    def get_headers(self, endpoint, body):

        timestamp = str(time.time())
        payload = '{timestamp}/{version}/{endpoint}{body}'.format(
            timestamp=timestamp,
            version=self.API_VERSION,
            endpoint=endpoint,
            body=body
        )
        signature = hmac.new(
            self.api_secret.encode(),
            payload.encode(),
            hashlib.sha384
        ).hexdigest()

        return {
            'X-MKT-APIKEY': self.api_key,
            'X-MKT-SIGNATURE': signature,
            'X-MKT-TIMESTAMP': timestamp
        }

    def get(self, endpoint, params=None, headers=None):

        return requests.get(
            '{}/{}/{}'.format(self.BASE_URL, self.API_VERSION, endpoint),
            params=params,
            headers=headers
        ).json()

    def private_get(self, endpoint, params=None):

        self.check_has_tokens()
        headers = self.get_headers(endpoint, '')
        return self.get(endpoint, params=params, headers=headers)

    def post(self, endpoint, payload):

        self.check_has_tokens()
        body = [
            str(p[1]) for p in sorted(payload.items(), key=lambda p: p[0])
        ]
        headers = self.get_headers(endpoint, reduce(str.__add__, body))
        return requests.post(
            '{}/{}/{}'.format(self.BASE_URL, self.API_VERSION, endpoint),
            data=payload,
            headers=headers
        ).json()

    def markets(self):

        return self.get(self.ENDPOINT_MARKETS)

    def ticker(self):

        return self.get(self.ENDPOINT_TICKER)

    def book(self, market, order_type, page=0, limit=20):

        params = {
            'market': market,
            'type': order_type,
            'page': page,
            'limit': limit
        }
        return self.get(self.ENDPOINT_BOOK, params=params)

    def trades(self, market, start=None, end=None, page=0, limit=20):

        params = {
            'market': market,
            'page': page,
            'limit': limit
        }
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        return self.get(self.ENDPOINT_TRADES, params=params)

    def balance(self):

        return self.private_get(self.ENDPOINT_BALANCE)

    @property
    def orders(self):

        return CryptoMKTOrdersAPI(self)


class CryptoMKTOrdersAPI(object):

    ENDPOINT_ACTIVE = 'orders/active'
    ENDPOINT_CANCEL = 'orders/cancel'
    ENDPOINT_CREATE = 'orders/create'
    ENDPOINT_EXECUTED = 'orders/executed'
    ENDPOINT_STATUS = 'orders/status'

    def __init__(self, api_wrapper):

        self.api = api_wrapper

    def active(self, market, page=0, limit=20):

        params = {
            'market': market,
            'page': page,
            'limit': limit
        }
        return self.api.private_get(self.ENDPOINT_ACTIVE, params)

    def executed(self, market, page=0, limit=20):

        params = {
            'market': market,
            'page': page,
            'limit': limit
        }
        return self.api.private_get(self.ENDPOINT_EXECUTED, params)

    def create(self, market, type, amount, price):

        params = {
            'market': market,
            'type': type,
            'amount': amount,
            'price': price
        }
        return self.api.post(self.ENDPOINT_CREATE, params)

    def cancel(self, order_id):

        return self.api.post(self.ENDPOINT_CANCEL, {'id': order_id})

    def status(self, order_id):

        return self.api.private_get(self.ENDPOINT_STATUS, {'id': order_id})


class InvalidTokensException(Exception):
    pass
