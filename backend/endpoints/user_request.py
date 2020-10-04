import logging
from flask import jsonify

from models import Request

log = logging.getLogger("user_request")


def create_request(request_json):
    """Creates and persists a new user request into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the user request details.
        example {
                  "beneficiary": 123456,
                  "user": 123456,
                  "status": "new",
                  "secret": "345%443$$",
                  "urgent": false,
                  "comments": "string",
                  "has_symptoms": false,
                  "cluster": 34,
                  "created_at": "2020-10-04T21:31:16.741Z"
                }
    Returns
    -------
    200:
        If the request was successfully created and saved.
    400:
        If the request wasn't created or saved, and there was raised some exception.
    """
    try:
        user_request_data = request_json
        log.debug(request_json)
        user_request = Request(**user_request_data)
        user_request.save()
        return jsonify({"response": "Request created successfully"}), 201
    except Exception as error:
        log.error("Error while creating request {}".format(error))
        return jsonify({"error": str(error)}), 400
