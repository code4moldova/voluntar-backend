import pytest
from flask_httpauth import HTTPBasicAuth

from server import create_application


@pytest.fixture
def app():
    auth = HTTPBasicAuth()
    application = create_application(auth)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="class")
def api_client(request):
    auth = HTTPBasicAuth()
    request.cls.client = create_application(auth).test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
