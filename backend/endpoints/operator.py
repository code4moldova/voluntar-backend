from datetime import datetime as dt
from datetime import timedelta
from typing import Optional

from flask import jsonify, request
from flask.views import MethodView

from config import MIN_PASSWORD_LEN, PassHash
from models import Beneficiary, Operator
from utils import search, common


def registerOperator(requestjson, created_by):
    """create a new user"""
    new_operator = requestjson
    if len(created_by) > 30:
        user = Operator.verify_auth_token(created_by)
        created_by = user.get().clean_data()["email"]
    # TODO: get authenticated operator and assignee to new Operator
    # new_operator["created_by"] = authenticated_oprator
    try:
        assert (
            len(new_operator["password"]) >= MIN_PASSWORD_LEN
        ), f"Password is to short, min length is {MIN_PASSWORD_LEN}"
        new_operator["password"] = PassHash.hash(new_operator["password"])
        new_operator["created_by"] = created_by
        new_operator["created_at"] = dt.utcnow()
        assert not Operator.objects(email=new_operator["email"]), "user with this email already exists"
        comment = Operator(**new_operator)
        comment.save()
        return jsonify({"response": "success", "user": comment.clean_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def updateOperator(requestjson, operator_id, delete=False):
    """update a single user by id"""
    print(operator_id, "---")
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
        Operator.objects(id=operator_id).get().update(**update)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def getOperators(operator_id, active: Optional[str]):
    is_active = common.toBool(active)
    try:
        if operator_id:
            operator = Operator.objects(id=operator_id).get().clean_data()
            return jsonify(operator)
        elif is_active:
            operator = [v.clean_data() for v in Operator.objects(is_active=is_active).all()]
            return jsonify({"list": operator})
        else:
            operator = [v.clean_data() for v in Operator.objects().all()]
            return jsonify({"list": operator})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def get_operators_by_filters(filters, pages=0, per_page=10000):
    """ Searches users in database for the given parameters.

    Parameters
    ----------
    filters : dict
        A dictionary including name of filters as key and their values.
    pages : int
        Number of pages what would be returned.
    per_page : int
        Number of records returned per page.

    Returns
    -------
    Response
        A JSON response like this:

        {
            "count": "5",
            "list": [...]
        }
    """
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            case = ["is_active", "roles"]

            for key, value in filters.items():
                if key not in case and key != "query":
                    return jsonify({"error": key + " key can't be found"}), 400
                if key in case:
                    if key == "roles":
                        flt[key + "__in"] = [value]
                    elif key == "is_active":
                        flt[key] = True if value == "true" else False
                    else:
                        flt[key] = value

            if "query" in filters.keys() and len(filters["query"]) > 0:
                query_search_fields = ["first_name", "last_name", "phone"]
                obj = search.model_keywords_search(Operator, query_search_fields, filters["query"].split()).filter(
                    **flt
                )
            else:
                obj = Operator.objects().filter(**flt)

            users = [user.clean_data() for user in obj.order_by("-created_at").skip(offset).limit(item_per_age)]

            return jsonify({"list": users, "count": obj.count()})
        else:
            obj = Operator.objects().order_by("-created_at")
            users = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": users, "count": obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def getToken(username):
    operator = Operator.objects(email=username, is_active=True)  # .get()#.clean_data()
    if operator:
        return operator.get().generate_auth_token(), operator.get().clean_data()
    # print(operator)
    # g.user = operator
    return None


def verifyUser(username, password):
    user = Operator.verify_auth_token(username)  # username_or_token
    if not user:
        operator = Operator.objects(email=username, is_active=True)  # .get()#.clean_data()
        if operator:
            return operator.get().check_password(password)
        # print(operator)
        return False
    # g.user = operator
    return True
