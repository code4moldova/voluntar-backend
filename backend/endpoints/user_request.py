import logging

from flask import jsonify

from models import Request, Beneficiary
from users import UserDocument

log = logging.getLogger("user_request")

beneficiary_fields = [
    "first_name",
    "last_name",
    "phone",
    "landline",
    "age",
    "zone",
    "address",
    "special_condition",
    "latitude",
    "longitude",
]


def create_request(request_json, created_by):
    """Creates and persists a new user request into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the user request details.
        example1 {
                  "beneficiary": "123456",
                  "type":"grocery",
                  "status": "new",
                  "secret": "345%443$$",
                  "urgent": false,
                  "comments": "string",
                  "has_symptoms": false
                }
        example2 {
                  "beneficiary": "123456",
                  "type":"grocery",
                  "status": "new",
                  "secret": "345%443$$",
                  "urgent": false,
                  "comments": "string",
                  "has_symptoms": false,
                  "first_name": "str",
                  "last_name": "str",
                  "phone": "68633333",
                  "landline": "68338333",
                  "age": 60,
                  "zone": "botanica",
                  "address": "dacia"
                }
    Returns
    -------
    200:
        If the request was successfully created and saved.
    400:
        If the request wasn't created or saved, and there was raised some exception.
    """
    if len(created_by) > 30:
        user = UserDocument.verify_auth_token(created_by)
        created_by = user.get().clean_data()["email"]
    try:
        created_by = UserDocument.objects.get(email=created_by)
        if "beneficiary" in request_json:
            beneficiary = Beneficiary.objects.get(id=request_json["beneficiary"])
            if beneficiary is None:
                return jsonify({"error": "beneficiary not found"}), 400
        else:
            new_beneficiary = {k: request_json[k] for k in beneficiary_fields if k in request_json}
            new_beneficiary["created_by"] = created_by.clean_data()["email"]
            beneficiary = Beneficiary(**new_beneficiary)
            beneficiary.save()

        user_request_data = {k: v for k, v in request_json.items() if k not in beneficiary_fields}
        user_request_data["user"] = created_by
        user_request_data["beneficiary"] = beneficiary
        log.debug(request_json)
        user_request = Request(**user_request_data)
        user_request.save()
        return jsonify({"response": "success", "user": user_request.clean_data()}), 201
    except Exception as error:
        log.error("Error while creating request {}".format(error))
        return jsonify({"error": str(error)}), 400
