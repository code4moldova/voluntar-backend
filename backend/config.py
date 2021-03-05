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
DB_HOST = os.environ.get("DB_HOST", "mongodb://mongodb_container:27017")

MIN_PASSWORD_LEN = 6
