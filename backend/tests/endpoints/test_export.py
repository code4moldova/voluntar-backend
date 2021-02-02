from tests import ApiTestCase
from tests.factories import BeneficiaryFactory, OperatorFactory


class TestExportCsvBeneficiaries(ApiTestCase):
    def test_export_csv_beneficiaries(self):
        operator = OperatorFactory()
        operator.save()

        BeneficiaryFactory(first_name="Ion", last_name="Neculce", age=50,).save()

        response = self.get(url="/api/export/csv/beneficiaries", user=operator)

        assert response.status_code == 200
        body = response.data.decode("utf-8")
        assert "last_name" in body
        assert "first_name" in body
        assert "Ion" in body
        assert "Neculce" in body
