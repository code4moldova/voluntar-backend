from flask import Flask

from config import FLASK_ENV
from endpoints.welcome import register as welcome_register
from endpoints.auth import register as auth_register
from seeds import init_app as seed_cli


def create_application():
    app = Flask(__name__)

    if FLASK_ENV == 'test':
        app.config.from_mapping({'TESTING': True})

    if FLASK_ENV == 'development':
        seed_cli(app)

    # endpoints
    welcome_register(app)
    auth_register(app)

    return app
