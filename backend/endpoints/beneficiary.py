import logging
from datetime import datetime as dt

from flask import jsonify
from mongoengine import Q

from endpoints import volunteer
from models import Beneficiary
from models import Operator

from utils import search

log = logging.getLogger("back")


def registerBeneficiary(requestjson, created_by):
    """create a new beneficiary"""
    new_beneficiary = requestjson
    if len(created_by) > 30:
        user = Operator.verify_auth_token(created_by)
        created_by = user.get().clean_data()["email"]
    try:
        if "phone" not in new_beneficiary and "landline" not in new_beneficiary:
            assert False, "Need at least one phone number"
        new_beneficiary["created_by"] = created_by
        new_beneficiary["created_at"] = dt.utcnow()
        new_beneficiary = Beneficiary(**new_beneficiary)
        new_beneficiary.save()
        return jsonify({"response": "success", "user": new_beneficiary.clean_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def updateBeneficiary(requestjson, beneficiary_id, delete=False):
    """update a single user by id"""
    update = {}
    if not delete:
        for key, value in requestjson.items():
            if key == "_id":
                continue
            update[f"set__{key}"] = value
    else:
        update["set__is_active"] = False

    try:
        obj = Beneficiary.objects(id=beneficiary_id).get()
        data = obj.clean_data()  # and not data['is_active']
        if "set__status" in update and update["set__status"].lower() == "cancelled":
            # if the volunteer refused the request, delete the link
            volunteer_updates = {"push__offer_list": {"id": beneficiary_id, "offer": data["offer"], "cancelled": True}}
            volunteer.update_volunteer(requestjson["volunteer"], volunteer_updates)
            update["set__volunteer"] = ""
            update["set__status"] = update["set__status"].lower()
        obj.update(**update)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def getBeneficiary(args):
    try:
        id = args.get("id")
        if id:
            beneficiary = Beneficiary.objects(id=id).get().clean_data()
            return jsonify(beneficiary)
        else:
            try:
                is_active = bool(args.get("is_active", None, bool))
                first_name = args.get("first_name", None, str)
                phone = args.get("phone", None, int)
                created_date_start = args.get("created_date_start", None, dt)
                created_date_end = args.get("created_date_end", None, dt)
                item_start = args.get("item_start", None, int)
                item_end = args.get("item_end", None, int)
            except Exception:
                return jsonify({"error": "Incorrect arg(s)."})

            ben_objs = Beneficiary.objects()
            if is_active:
                ben_objs.filter(is_active=is_active)
            if first_name:
                ben_objs.filter(first_name=first_name)
            if phone:
                ben_objs.filter(phone=phone)
            if created_date_start and created_date_end:
                ben_objs.filter((Q(created_at__gte=created_date_start) & Q(created_at__lte=created_date_end)))
            count = ben_objs.all().count()
            if item_start and item_end:
                ben_objs.skip(item_start).limit(item_end)
            beneficiaries = [v.clean_data() for v in ben_objs.all()]
            return jsonify({"list": beneficiaries}, {"pagination": {"count_of_records": count}})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def get_beneficiaries_by_filters(filters, pages=0, per_page=10000):
    try:
        item_per_age = int(per_page)
        offset = (int(pages) - 1) * item_per_age
        if len(filters) > 0:
            flt = {}
            search_query = {}
            to_bool = {"true": True, "false": False}
            case = ["query", "zone", "is_active", "black_list", "status", "phone", "landline"]

            for key, value in filters.items():
                if key not in case:
                    return jsonify({"error": key + " key can't be found"}), 400
                elif key == "query" and value:
                    search_query = value
                elif key in ["is_active", "black_list"]:
                    if value.lower() not in to_bool:
                        return jsonify({"error": "boolean " + key + " accept only true/false values"}), 400
                    else:
                        flt[key] = to_bool[value.lower()]
                elif value:
                    flt[key] = value

            if len(search_query):
                query_search_fields = ["first_name", "last_name", "phone", "landline"]
                obj = search.model_keywords_search(Beneficiary, query_search_fields, search_query.split()).filter(**flt)
            else:
                obj = Beneficiary.objects().filter(**flt)

            beneficiaries = [v.clean_data() for v in obj.order_by("-created_at").skip(offset).limit(item_per_age)]

            return jsonify({"list": beneficiaries, "count": obj.count()})
        else:
            obj = Beneficiary.objects().order_by("-created_at")
            beneficiaries = [v.clean_data() for v in obj.skip(offset).limit(item_per_age)]
            return jsonify({"list": beneficiaries, "count": obj.count()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400
