from flask import jsonify

from endpoints import getToken


def register(app, auth):
    # Authentication
    @app.route("/api/token", methods=["GET", "POST"])
    @auth.login_required
    def get_auth_token():
        token, data = getToken(auth.username())  # g.user.generate_auth_token()
        return jsonify({"token": token.decode("ascii")})
