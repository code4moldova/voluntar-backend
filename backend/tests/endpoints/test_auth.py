import json

from tests import ApiTestCase
from tests.factories import OperatorFactory


class TestAuth(ApiTestCase):
    def test_token(self):
        operator = OperatorFactory()
        operator.save()

        response = self.get(url="/api/token", user=operator)

        assert response.status_code == 200
        results = json.loads(response.data)
        assert "token" in results
