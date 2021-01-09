import os
from datetime import datetime

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from mongoengine import BooleanField, DateTimeField, Document, EmailField, FloatField, IntField, ListField, StringField

from config import PassHash
from models.enums import UserRole, WeekDay


class User(Document):
    first_name = StringField(max_length=50, default="No_First")
    last_name = StringField(max_length=50, default="No_Last")
    email = EmailField(required=True)
    password = StringField(required=True, min_length=6)
    phone = StringField(max_length=8, regex=r"\d")
    roles = ListField(StringField(choices=[role.value for role in UserRole]), default=[])
    availability_hours_start = IntField(min_value=8, max_value=20)
    availability_hours_end = IntField(min_value=8, max_value=20)
    availability_days = ListField(StringField(choices=[weekday.value for weekday in WeekDay]), default=[])
    is_active = BooleanField(default=True)  # we don't delete users just deactivating them
    created_at = DateTimeField(default=datetime.now())
    last_access = DateTimeField(default=datetime.now())
    created_by = StringField(max_length=500)

    # Will be deleted after frontend changes
    role = ListField(default=[])
    address = StringField(required=True, min_length=4)
    logins = ListField(default=[])
    meta = {"allow_inheritance": True}

    def clean_data(self) -> dict:
        data = self.to_mongo()
        if "password" in data and data["password"]:
            del data["password"]
        data["_id"] = str(data["_id"])
        return data

    def generate_auth_token(self, expiration=60000):
        secret = os.environ["SECRET_KEY"]
        s = Serializer(secret, expires_in=expiration)
        User.objects(id=str(self.id)).get().update(last_access=datetime.now())
        obj = self.clean_data()
        del obj["role"]
        for k in obj.keys():
            if type(obj[k]) is datetime:
                del obj[k]
        obj["id"] = obj["_id"]
        del obj["_id"]
        return s.dumps(obj)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(os.environ["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.objects(id=data["id"])
        return user

    def include_data(self, includelist) -> dict:
        data = self.to_mongo()
        out = {}
        for k in includelist:
            out[k] = data[k] if k in data else ""
        return out

    def check_password(self, password) -> bool:
        data = self.to_mongo()
        return PassHash.verify(password, data["password"])


# Will be deleted after frontend changes
class Operator(User):
    created_by = StringField(max_length=500)
    role = ListField(default=["fixer"])  # TODO remove the field
    roles = ListField(default=["fixer"])
    address = StringField(max_length=500)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    city = StringField(max_length=500, required=False)
