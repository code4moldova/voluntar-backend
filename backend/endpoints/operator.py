from datetime import datetime as dt
from datetime import timedelta

from flask import jsonify, request
from flask.views import MethodView

from config import MIN_PASSWORD_LEN, PassHash
from models import Beneficiary, Operator
from utils import search


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


def getOperators(operator_id):
    try:
        if operator_id:
            operator = Operator.objects(id=operator_id).get().clean_data()
            return jsonify(operator)
        else:
            operator = [v.clean_data() for v in Operator.objects(is_active=True).all()]
            return jsonify({"list": operator})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def get_active_operator(days=2):
    days_diff = dt.now() - timedelta(days=days)
    pipeline_used_fixers = [
        {"$match": {"status": "done", "created_at": {"$gte": days_diff}}},
        {"$sort": {"created_at": 1}},
        {"$group": {"_id": "$fixer", "count": {"$sum": 1}}},
    ]
    fixers = []
    for f in Beneficiary.objects().aggregate(pipeline_used_fixers):
        fixers.append(f)

    available_fixers = [
        v.clean_data() for v in Operator.objects(is_active=True, role="fixer", created_at__gte=days_diff)
    ]
    available_fixers = [{"_id": af.get("_id")} for af in available_fixers]
    if len(fixers) != 0 and len(fixers) == len(available_fixers):
        return fixers[0].get("_id")
    else:
        fixers_ids = [val["_id"] for val in fixers]
        fixer_id = None
        for af in available_fixers:
            fixer_id = af.get("_id")
            if fixer_id not in fixers_ids:
                break
        return fixer_id


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

            users = [user.clean_data() for user in obj.skip(offset).limit(item_per_age)]

            return jsonify({"list": users, "count": obj.count()})
        else:
            obj = Operator.objects()
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


class OperatorAPI(MethodView):
    def get(self, operator_id: str):
        try:
            if operator_id:
                operator = Operator.objects(id=operator_id).get().clean_data()
                return jsonify(operator)
            else:
                operators = [v.clean_data() for v in Operator.objects(is_active=True).all()]
                return jsonify({"list": operators})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def post(self):
        """create a new user"""
        new_Operator = request.json
        # TODO: get authenticated operator and assignee to new Operator
        # new_Operator["created_by"] = authenticated_oprator
        try:
            assert (
                len(new_Operator["password"]) >= MIN_PASSWORD_LEN
            ), f"Password is to short, min length is {MIN_PASSWORD_LEN}"
            new_Operator["password"] = PassHash.hash(new_Operator["password"])
            comment = Operator(**new_Operator)
            comment.save()
            return jsonify({"response": "success"})
        except Exception as error:
            return jsonify({"error": str(error)}), 400

    def delete(self, operator_id):
        """delete a single user by id"""
        return self.put(operator_id, delete=True)

    def put(self, operator_id, delete=False):
        """update a single user by id"""
        update = {}
        if not delete:
            for key, value in request.json:
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
