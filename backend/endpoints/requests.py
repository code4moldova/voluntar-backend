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
            case = ["first_name", "last_name", "phone", "zone", "created_at", "pages", "page_size"]

            for key, value in filters.items():
                if key not in case:
                    return jsonify({"error": key + " key can't be found"}), 400
                elif key == "pages":
                    pages = int(value)
                elif key == "page_size":
                    page_size = int(value)
                elif value:
                    flt[key] = value

            beneficiaries = Beneficiary.objects().filter(**flt)

            request_objects = Request.objects(beneficiary__in=beneficiaries).all()

            offset = (int(pages) - 1) * page_size

            requests = [v.clean_data() for v in request_objects.skip(offset).limit(page_size)]

            total_count = request_objects.count()
            page_count = math.ceil(total_count / page_size)

            return jsonify({"metadata": {"page": pages, "page_size": page_size, "page_count": page_count,
                                         "total_count": total_count},
                            "records": requests})
        else:
            obj = Request.objects()

            total_count = obj.count()
            offset = (int(pages) - 1) * page_size
            page_count = math.ceil(total_count / page_size)

            requests = [v.clean_data() for v in obj.skip(offset).limit(page_size)]
            return jsonify({"metadata": {"page": pages, "page_size": page_size, "page_count": page_count, "total_count": total_count},
                            "records": requests})
    except Exception as error:
        return jsonify({"error": str(error)}), 400
