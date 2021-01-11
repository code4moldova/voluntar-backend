from services.table_list import BeneficiaryList
from tests import DbTestCase
from tests.factories import BeneficiaryFactory


class TestBeneficiaryList(DbTestCase):
    def test_run(self):
        users = [
            BeneficiaryFactory(first_name="Ion", last_name="Neculce", age=50, address="B", zone_address="A"),
            BeneficiaryFactory(
                first_name="Grigore", last_name="Ureche", age=119, address="B", zone_address="A", have_money=False,
            ),
        ]

        for user in users:
            user.save()

        rows = BeneficiaryList().run()
        self.assertEqual(["last_name", "first_name", "age"], rows[0][:3])
        self.assertEqual(len(rows), 3)
