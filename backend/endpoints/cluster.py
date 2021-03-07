from models import Request, Volunteer, Cluster
from flask import jsonify
from utils import volunteer_utils as vu


def register_cluster(request_json):
    """Creates and persists a new cluster into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the cluster details.
        example {
                  "volunteer": "volunteer_id",
                  "request_list": ['request_id_1', 'request_id_2', ....],
                  "created_at":  "2020-09-10T21:31:16.741Z"
                }

    Returns
    -------
    201:
        If the cluster was successful created and saved.
    400:
        If the cluster wasn't created or saved, and there was raised some exception.
    """

    try:
        volunteer = Volunteer.objects.get(id=request_json["volunteer"])
        if volunteer is None:
            return jsonify({"error": "Volunteer is not found"}), 400

        request_list = request_json["request_list"]
        if len(request_list) == 0:
            return jsonify({"error": "request_list is empty"}), 400

        for request_id in request_list:
            request = Request.objects.get(id=request_id, status="confirmed")
            if request is None:
                return jsonify({"error": "request {} 's status is not confirmed".format(request_id)}), 400

        new_cluster = Cluster(volunteer=volunteer)
        new_cluster.save()

        for request_id in request_list:
            request = Request.objects.get(id=request_id)
            request.cluster = new_cluster
            request.status = "in_process"
            request.save()

        vu.send_email(new_cluster.clean_data()["_id"], volunteer.clean_data()["email"])

        return jsonify({"response": "success", "cluster": new_cluster.clean_data()}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 400
