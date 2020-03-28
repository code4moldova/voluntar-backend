# compose_flask/app.py
import argparse
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Python-Flask-REST"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


@app.route('/')
def hello():
    return ("Hello world")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)