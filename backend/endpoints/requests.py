from flask import request, jsonify

from models.request_model import Request
from services.request_service import requests_by_filters


def register(app, auth):
    @app.route("/api/requests/filters/<page>/<per_page>", methods=["GET"])
    @auth.login_required
    def get_requests_by_filters(page=1, per_page=10):
        return requests_by_filters(request.args, page, per_page)


def get_requests_by_id(request_id):
    try:
        obj = Request.objects(id=request_id).get()
        return jsonify(obj.clean_data()), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 400
