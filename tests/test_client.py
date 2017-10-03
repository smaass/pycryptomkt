import unittest

from pycryptomkt.client import InvalidTokensException, CryptoMKT


class CryptoMKTTestCase(unittest.TestCase):

    def test_tokens(self):

        client = CryptoMKT()
        self.assertRaises(
            InvalidTokensException,
            lambda: client.orders.active('ETHCLP')
        )
