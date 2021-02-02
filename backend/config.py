from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from passlib.hash import sha256_crypt as PassHash
import os

FLASK_ENV = os.environ.get("FLASK_ENV", "development")

# swagger specific
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.yaml"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "Python-Flask-REST"})

DB_NAME = "covid-19"
DB_ADDRESS = os.environ.get("DB_HOST", "mongodb_container:27017")
DB_USERNAME = os.environ.get("DB_USERNAME")
if DB_USERNAME is None:
    DB_HOST = f"mongodb+srv://{DB_USERNAME}:{os.environ.get('DB_PASSWORD', '123456')}@{DB_ADDRESS}"
else:
    DB_HOST = f"mongodb://{DB_ADDRESS}"

MIN_PASSWORD_LEN = 6
