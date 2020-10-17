import logging
from flask import jsonify

from models import Request, User, Beneficiary, Cluster, Operator

log = logging.getLogger("user_request")


def create_request(request_json, created_by):
    """Creates and persists a new user request into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the user request details.
        example {
                  "beneficiary": "123456",
                  "type":"grocery",
                  "status": "new",
                  "secret": "345%443$$",
                  "urgent": false,
                  "comments": "string",
                  "has_symptoms": false
                }
    Returns
    -------
    200:
        If the request was successfully created and saved.
    400:
        If the request wasn't created or saved, and there was raised some exception.
    """
    if len(created_by) > 30:
        user = Operator.verify_auth_token(created_by)
        created_by = user.get().clean_data()["email"]
    try:
        created_by = Operator.objects.get(email=created_by)
        beneficiary = Beneficiary.objects.get(id=request_json['beneficiary'])
        if beneficiary is None:
          return jsonify({"error": 'beneficiary not found'}), 400
        user_request_data = request_json
        user_request_data["user"] = created_by
        user_request_data["beneficiary"] = beneficiary
        log.debug(request_json)
        user_request = Request(**user_request_data)
        user_request.save()
        return jsonify({"response": "success", "user": user_request.clean_data()}), 201
    except Exception as error:
        log.error("Error while creating request {}".format(error))
        return jsonify({"error": str(error)}), 400

