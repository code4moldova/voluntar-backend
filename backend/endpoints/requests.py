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

    @app.route("/api/cluster/<cluster_id>", methods=["GET"])
    def get_requests_by_cluster(cluster_id):
        return requests_by_filters(dict(cluster_id=cluster_id), 1, 100)


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


def update_request_status(request_id, cluster_id, updates):
    """Updates a request by ID and check that cluster_id is correct.

        Parameters
        ----------
        request_id : str
            A string representing request ID.
        updates : dict just with properties: status or comment
            A dictionary including name of fields as key and their values for updating.
        """
    try:
        updates_allowed = {k: updates[k] for k in ["status", "comments"] if k in updates}
        r = Request.objects(id=request_id)
        if r and str(r.get().cluster.id) == cluster_id:
            r.get().update(**updates_allowed)
            return jsonify({"response": "success"})
        else:
            return jsonify({"error": "cluster_id or _id is not correct"}), 400
    except Exception as error:
        log.error("An error occurred on updating Request. {}".format(str(error)))
        return jsonify({"error": str(error)}), 400


def get_requests_by_id(request_id):
    try:
        obj = Request.objects(id=request_id).get()
        return jsonify(obj.clean_data()), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 400
