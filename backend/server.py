from flask import Flask
from flask_httpauth import HTTPBasicAuth

from config import FLASK_ENV
from endpoints import verifyUser
from endpoints.welcome import register as welcome_register
from endpoints.auth import register as auth_register
from endpoints.export import register as export_register
from endpoints.import_csv import register as import_register
from endpoints.requests import register as request_register
from seeds import init_app as seed_cli


def create_application():
    app = Flask(__name__)

    if FLASK_ENV == "test":
        app.config.from_mapping({"TESTING": True})

    if FLASK_ENV == "development":
        seed_cli(app)

    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        return verifyUser(username, password)

    # endpoints
    welcome_register(app)
    auth_register(app, auth)
    request_register(app, auth)
    export_register(app, auth)
    import_register(app, auth)

    return app
