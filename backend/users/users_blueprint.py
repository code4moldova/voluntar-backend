__strict__ = True

from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth


def users_blueprint(_: HTTPBasicAuth):
    bp = Blueprint(__name__, "users")

    @bp.route("", methods=["GET"])
    def get_all_users():
        page = int(request.args.get('page') or 0)
        per_page = int(request.args.get('pageSize') or 10)
        offset = page * per_page

        return ""

    return bp
