from flask import Flask

from config import FLASK_ENV
from endpoints.welcome import register as welcome_register


def create_application():
    app = Flask(__name__)

    if FLASK_ENV == 'test':
        app.config.from_mapping({'TESTING': True})

    welcome_register(app)

    return app
