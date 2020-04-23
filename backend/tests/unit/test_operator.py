from endpoints import operator
from models import Beneficiary
from tests import DbTestCase


class TestOperator(DbTestCase):
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
        beneficiary.save()
        # Execute
        result = operator.get_active_operator()

        # Validate
        assert result is None
