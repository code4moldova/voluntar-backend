from unittest import TestCase

from mongoengine import connect, disconnect


class DbTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        connect('test', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()
