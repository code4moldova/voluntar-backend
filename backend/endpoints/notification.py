from flask import jsonify

from models import Notification, Request, NotificationUser


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
        NotificationUser.assign_notification_to_users(self=new_notification, status="new")
        return jsonify({"response": "success", "notification": new_notification.clean_data()}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def get_notifications_by_filters(filters, pages=1, per_page=10):
    """Returns notifications according to pagination and filters.

    Parameters
    ----------
    filters : list
        List of search parameters from url query

    pages : int
        Number pages to show

    per_page : int
        Number results per page

    Returns
    -------
    list
        JSON with count of results and list of results

    """
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            case = ["status", "user"]

            for key, value in filters.items():
                if key not in case:
                    return jsonify({"error": key + " key can't be found"}), 400
                elif key in case and value:
                    flt[key] = value

            notification_user = NotificationUser.objects(**flt)
            notifications = [
                v.notification.clean_data()
                for v in notification_user.order_by("-created_at").skip(offset).limit(item_per_age)
            ]
            return jsonify({"list": notifications, "count": notification_user.count()})
        else:
            obj = Notification.objects().order_by("-created_at")
            notifications = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": notifications, "count": obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400
