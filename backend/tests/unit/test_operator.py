from endpoints import operator
from tests import DbTestCase
from tests.factories import BeneficiaryFactory


class TestOperator(DbTestCase):
    def test_get_active_operator_none_result(self):
        # Setup
        beneficiary = BeneficiaryFactory(first_name="John", last_name="Travolta")
        beneficiary.save()
        # Execute
        result = operator.get_active_operator()

        # Validate
        assert result is None
