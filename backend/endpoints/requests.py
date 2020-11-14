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


def get_requests_by_id(request_id):
    try:
        obj = Request.objects(id=request_id).get()
        return jsonify(obj.clean_data()), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def get_requests_by_query_filters(filters):
    pages = 1
    page_size = 30
    try:
        if len(filters) > 0:
            flt = {}
            case = ["first_name", "last_name", "phone", "zone", "created_at"]

            for key, value in filters.items():
                if key not in case:
                    return jsonify({"error": key + " key can't be found"}), 400
                elif value:
                    flt[key] = value

            beneficiaries = [v.clean_data() for v in obj.order_by("-created_at").skip(offset).limit(item_per_age)]

            return jsonify({"list": beneficiaries, "count": obj.count()})
        else:
            obj = Request.objects()
            requests = [v.clean_data() for v in obj.skip(pages).limit(page_size)]
            return jsonify({"metadata": {"page": pages, "page_size": page_size, "page_count": "1", "total_count": obj.count()},
                            "records": requests})
    except Exception as error:
        return jsonify({"error": str(error)}), 400
