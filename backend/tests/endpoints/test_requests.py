import datetime
import json

from tests import ApiTestCase
from tests.factories import BeneficiaryFactory, ClusterFactory, OperatorFactory, RequestFactory


class TestRequests(ApiTestCase):
    def test_filter_by_beneficiary(self):
        operator = OperatorFactory()
        operator.save()

        beneficiary = BeneficiaryFactory(first_name="Ion", last_name="Neculce", age=50,).save()
        req1 = RequestFactory(beneficiary=beneficiary, user=operator, created_at="2020-01-01")
        req1.save()

        cluster = ClusterFactory()
        cluster.volunteer.save()
        cluster.save()
        req2 = RequestFactory(
            beneficiary=beneficiary, user=operator, status="in_process", created_at="2020-02-02", cluster=cluster,
        )
        req2.save()

        req3 = RequestFactory()
        req3.user.save()
        req3.beneficiary.save()
        req3.save()

        response = self.get(url=f"/api/requests/filters/1/10?b_id={beneficiary.id}", user=operator)

        assert response.status_code == 200
        self.assertEqual(
            dict(
                count=2,
                list=[
                    {
                        "_id": str(req2.id),
                        "status": "in_process",
                        "urgent": False,
                        "comments": None,
                        "has_symptoms": False,
                        "created_at": "Sun, 02 Feb 2020 00:00:00 GMT",
                        "volunteer": {
                            "_id": str(req2.cluster.volunteer.id),
                            "first_name": req2.cluster.volunteer.first_name,
                            "last_name": req2.cluster.volunteer.last_name,
                        },
                    },
                    {
                        "_id": str(req1.id),
                        "status": "new",
                        "urgent": False,
                        "comments": None,
                        "has_symptoms": False,
                        "created_at": "Wed, 01 Jan 2020 00:00:00 GMT",
                    },
                ],
            ),
            json.loads(response.data),
        )
