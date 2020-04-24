from flask import jsonify
from flask_httpauth import HTTPBasicAuth

from endpoints import getToken, verifyUser


def register(app):
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        return verifyUser(username, password)

    # Authentication
    @app.route('/api/token', methods=['GET', 'POST'])
    @auth.login_required
    def get_auth_token():
        token, data = getToken(auth.username())  # g.user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})
