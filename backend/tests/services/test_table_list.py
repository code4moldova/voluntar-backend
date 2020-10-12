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
        self.assertEqual(
            [
                [
                    "Nume",
                    "Prenume",
                    "Vîrsta",
                    "Are bani?",
                    "phone",
                    "address",
                    "zone_address",
                    "offer",
                    "comments",
                    "urgent",
                    "curator",
                    "has_disabilities",
                    "black_list",
                ],
                ["Neculce", "Ion", 50, 1, "11112222", "B", "A", "1", "", 0, 0, 0, 0],
                ["Ureche", "Grigore", 119, 0, "11112222", "B", "A", "1", "", 0, 0, 0, 0],
            ],
            rows,
        )
