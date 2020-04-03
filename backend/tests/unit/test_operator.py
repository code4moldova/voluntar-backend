import unittest
from endpoints import operator
from models import Beneficiary
from mongoengine import connect, disconnect


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect('test', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_get_active_operator_none_result(self):
        # Setup
        beneficiary = Beneficiary()
        beneficiary.first_name = 'John'
        beneficiary.last_name = 'Travolta'
        beneficiary.phone = '12345678'
        beneficiary.email = 'john@email.com'
        beneficiary.address = 'address'
        beneficiary.zone_address = 'zone'
        beneficiary.status = 'done'
        beneficiary.fixer = '123456'
        beneficiary.password = 'password'
        beneficiary.secret = 'secret'

        # Execute
        result = operator.get_active_operator()

        # Validate
        assert result is None


if __name__ == '__main__':
    unittest.main()
