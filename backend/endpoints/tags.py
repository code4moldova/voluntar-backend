from flask import jsonify

from config import PassHash
from models import Tags
from users import UserDocument
from models.enums import (
    VolunteerRole,
    VolunteerStatus,
    Zone,
    WeekDay,
    UserRole,
    SpecialCondition,
    RequestStatus,
    NotificationType,
    NotificationStatus,
    RequestType,
)

enums_list = dict(
    sector=Zone,
    VolunteerStatus=VolunteerStatus,
    VolunteerRole=VolunteerRole,
    Role=UserRole,
    SpecialCondition=SpecialCondition,
    RequestStatus=RequestStatus,
    RequestType=RequestType,
    NotificationType=NotificationType,
    NotificationStatus=NotificationStatus,
    Zone=Zone,
    WeekDay=WeekDay,
)


def registerTag(requestjson, created_by):
    """create a new user"""
    new_Tags = requestjson
    if len(created_by) > 30:
        user = UserDocument.verify_auth_token(created_by)
        created_by = user.get().clean_data()["email"]
    # TODO: get authenticated operator and assignee to new Tags
    # new_Tags["created_by"] = authenticated_oprator
    try:
        new_Tags["created_by"] = created_by  # g.user.get().clean_data()['_id']
        comment = Tags(**new_Tags)
        comment.save()
        return jsonify({"response": "success", "user": comment.clean_data()})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def updateTag(requestjson, tag_id, delete=False):
    """update a single user by id"""
    print(tag_id, "---")
    update = {}
    toBool = {"true": True, "false": False}
    if not delete:
        for key, value in requestjson.items():
            if key == "_id":
                continue
            if key == "password":
                value = PassHash.hash(value)
            update[f"set__{key}"] = value if value.lower() not in toBool else toBool[value.lower()]
    else:
        update["set__is_active"] = False

    try:
        Tags.objects(id=tag_id).get().update(**update)
        return jsonify({"response": "success"})
    except Exception as error:
        return jsonify({"error": str(error)}), 400


def getTags(tag_id, select, js=True):
    try:
        if tag_id:
            tags = Tags.objects(id=tag_id).get().clean_data()
            return jsonify(tags)
        elif select != "all":
            if select in enums_list:
                return jsonify(
                    [
                        {
                            "_id": i.name,
                            "created_by": "",
                            "en": "-",
                            "is_active": True,
                            "ro": i.value,
                            "ru": "",
                            "select": select,
                        }
                        for i in enums_list[select]
                    ]
                )
            if js:
                tags = [v.clean_data() for v in Tags.objects(is_active=True, select=select).all()]
                return jsonify({"list": tags})
            tags = [v.clean_data() for v in Tags.objects(select=select).order_by("-is_active").all()]
            return tags
        else:
            tags = [v.clean_data() for v in Tags.objects(is_active=True).all()]
            if js:
                return jsonify({"list": tags})
            return tags
    except Exception as error:
        return jsonify({"error": str(error)}), 400
