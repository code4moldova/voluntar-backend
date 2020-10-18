from models import Notification, Request
from flask import jsonify


def register_notification(request_json):
    """Creates and persists a new notification into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the notification details.
        example {
                  "request": "request_id",
                  "type": "new_request",
                  "subject": "string",
                  "created_at": "2020-09-10T21:31:16.741Z"
                }

    Returns
    -------
    201:
        If the notification was successful created and saved.
    400:
        If the notification wasn't created or saved, and there was raised some exception.
    """

    try:
        new_notification_data = request_json
        request = Request.objects.get(id=request_json["request"])
        if request is None:
            return jsonify({"error": "Request not found"}), 400
        new_notification = Notification(**new_notification_data)
        new_notification.save()
        return jsonify({"response": "success", "notification": new_notification.clean_data()}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 400
