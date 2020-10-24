import logging

from flask import request, jsonify

from models.request_model import Request
from services.request_service import requests_by_filters

log = logging.getLogger("back")


def register(app, auth):
    @app.route("/api/requests/filters/<page>/<per_page>", methods=["GET"])
    @auth.login_required
    def get_requests_by_filters(page=1, per_page=10):
        return requests_by_filters(request.args, page, per_page)


def update_request(request_id, updates):
    """Updates a request by ID.

        Parameters
        ----------
        request_id : str
            A string representing request ID.
        updates : dict
            A dictionary including name of fields as key and their values for updating.
        """
    try:
        updates.pop("_id")
        Request.objects(id=request_id).get().update(**updates)
        return jsonify({"response": "success"})
    except Exception as error:
        log.error("An error occurred on updating Request. {}".format(str(error)))
        return jsonify({"error": str(error)}), 400

