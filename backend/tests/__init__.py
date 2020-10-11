import base64
from unittest import TestCase
import pytest

from mongoengine import connect, disconnect


class DbTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        connect("test", host="mongomock://localhost")

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def setUp(self):
        self.maxDiff = None


@pytest.mark.usefixtures("api_client")
class ApiTestCase(DbTestCase):
    def get(self, url, user):
        encoded_pass = base64.b64encode(bytes(user.email + ":" + "123456", "ascii")).decode("ascii")

        response = self.client.get(url, headers={"Authorization": "Basic " + encoded_pass})

        return response
