from services.table_list import BeneficiaryList
from tests import DbTestCase
from tests.factories import BeneficiaryFactory


class TestBeneficiaryList(DbTestCase):
    def test_run(self):
        users = [
            BeneficiaryFactory(
                first_name='Ion',
                last_name='Neculce',
                age=50,
            ),
            BeneficiaryFactory(
                first_name='Grigore',
                last_name='Ureche',
                age=119,
                have_money=False,
            ),
        ]

        for user in users:
            user.save()

        rows = BeneficiaryList().run()
        self.assertEqual(
            [
                ['Nume', 'Prenume', 'Vîrsta', 'Are bani?'],
                ['Neculce', 'Ion', 50, 1],
                ['Ureche', 'Grigore', 119, 0]
            ],
            rows
        )
