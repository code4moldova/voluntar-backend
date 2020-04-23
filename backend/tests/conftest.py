import pytest

from server import create_application


@pytest.fixture
def app():
    application = create_application()
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
