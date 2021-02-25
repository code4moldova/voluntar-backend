import csv
import io
import logging
from datetime import datetime, timedelta
from datetime import datetime as dt

from flask import jsonify, make_response, json

from config import PassHash
from models import Beneficiary
from models import Operator
from models import Volunteer

from utils import volunteer_utils as vu
from utils import search

log = logging.getLogger("back")


def register_volunteer(request_json, created_by):
    """Creates and persists a new volunteer into database.

    Parameters
    ----------
    request_json : dict
        A dictionary representing the volunteer profile details.
    created_by : str
         A string representing either name of user who is going to create a new volunteer, or the token

    Returns
    -------
    200:
        If the volunteer was successful created and saved.
    400:
        If the volunteer wasn't created or saved, and there was raised some exception.
    """
    log.debug("Relay offer for req:%s from ", request_json)
    try:
        if not vu.is_email(created_by):
            user = Operator.verify_auth_token(created_by)
            created_by = user.get().clean_data()["email"]

        vu.exists_by_email(request_json["email"])
        new_volunteer_data = request_json
        new_volunteer_data["created_by"] = created_by
        new_volunteer = Volunteer(**new_volunteer_data)
        new_volunteer.save()
        return jsonify({"response": "success", "user": new_volunteer.clean_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def updateVolunteer(requestjson, volunteer_id, delete=False):
    """update a single user by id"""
    print(volunteer_id, "---")
    update = {}
    if not delete:
        for key, value in requestjson.items():
            if key == "_id":
                continue
            if key == "password":
                value = PassHash.hash(value)
            update[f"set__{key}"] = value
    else:
        update["set__is_active"] = False

    try:
        Volunteer.objects(id=volunteer_id).get().update(**update)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def update_volunteer(volunteer_id, updates):
    """Updates a volunteer by ID.

    Parameters
    ----------
    volunteer_id : str
        A string representing volunteer ID.
    updates : dict
        A dictionary including name of fields as key and their values for updating.
    """
    # todo: to delete
    try:
        Volunteer.objects(id=volunteer_id).get().update(**updates)
    except Exception as error:
        log.error("An error occurred on updating Volunteers. {}".format(error.message))


def getVolunteers(filters):
    try:
        if len(filters.getlist("id")) == 1:
            volunteer_id = filters.get("id")
            volunteer = Volunteer.objects(id=volunteer_id).get().clean_data()

            return jsonify(volunteer)
        elif len(filters.getlist("id")) > 1:
            volunteers = [
                Volunteer.objects(id=volunteer_id).get().clean_data() for volunteer_id in filters.getlist("id")
            ]
            return jsonify({"list": volunteers})
        else:
            volunteers = [v.clean_data() for v in Volunteer.objects(is_active=True).order_by("-created_at").all()]
            for i, volunteer in enumerate(volunteers):
                volunteers[i]["cases_solved"] = Beneficiary.objects(volunteer=volunteer["_id"]).count()
            return jsonify({"list": volunteers})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def utc_short_to_user_short(short_time):
    """Transform a short '%H:%M' time notation from UTC to the user's timezone
    :params short_time: str, timestamp in %H:%M format
    :returns: str, timestamp in the same format, but adapted to the user's timezone"""
    raw = datetime.strptime(short_time, "%H:%M")
    localized = raw + timedelta(hours=3)
    return localized.strftime("%H:%M")


def get_volunteers_by_filters(filters, pages=0, per_page=10000):
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            case = ["zone", "role", "status", "availability_days"]

            for key, value in filters.items():
                if key not in case and key != "query":
                    return jsonify({"error": key + " key can't be found"}), 400
                if key in case:
                    flt[key] = value

            if "query" in filters.keys() and len(filters["query"]) > 0:
                query_search_fields = ["first_name", "last_name", "phone"]
                obj = search.model_keywords_search(Volunteer, query_search_fields, filters["query"].split()).filter(
                    **flt
                )
            else:
                obj = Volunteer.objects().filter(**flt)

            volunteers = [v.clean_data() for v in obj.order_by("-created_at").skip(offset).limit(item_per_age)]

            return jsonify({"list": volunteers, "count": obj.count()})
        else:
            obj = Volunteer.objects().order_by("-created_at")
            volunteers = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": volunteers, "count": obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def deleteVolunteer(requestjson, volunteer_id):
    updateVolunteer(requestjson, volunteer_id, delete=True)
