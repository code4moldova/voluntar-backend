import calendar
import json
from datetime import datetime as dt
from enum import Enum

from mongoengine import (
    Document,
    StringField,
    IntField,
    EmailField,
    BooleanField,
    ListField,
    DateTimeField,
    DictField,
    FloatField,
    URLField,
    ReferenceField,
)
from config import PassHash

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
import os

from backend.models.beneficiary_model import Beneficiary
from backend.models.cluster_model import Cluster
from backend.models.user_model import User

FACEBOOK_URL_REGEX = r"http(?:s):\/\/(?:www\.)facebook\.com\/.+"


class Tags(Document):
    # TODO: Each volunteer must have a reference to operator that was created by
    # created_by = ReferenceField("operator")
    select = StringField(max_length=50)
    ro = StringField(max_length=500)
    ru = StringField(max_length=500)
    created_by = StringField(max_length=500)
    en = StringField(max_length=500)
    is_active = BooleanField(default=True)

    def clean_data(self) -> dict:
        data = self.to_mongo()
        if "password" in data and data["password"]:
            del data["password"]
        if "logins" in data:
            del data["logins"]
        data["_id"] = str(data["_id"])
        return data

    def generate_auth_token(self, expiration=60000):
        secret = os.environ["SECRET_KEY"]
        s = Serializer(secret, expires_in=expiration)
        User.objects(id=str(self.id)).get().update(last_access=dt.now)
        obj = self.clean_data()
        del obj["role"]
        for k in obj.keys():
            if type(obj[k]) is dt:
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

    def clean_data(self) -> dict:
        data = self.to_mongo()
        if "password" in data and data["password"]:
            del data["password"]
        if "logins" in data:
            del data["logins"]
        data["_id"] = str(data["_id"])
        return data

    def include_data(self, includelist) -> dict:
        data = self.to_mongo()
        out = {}
        for k in includelist:
            out[k] = data[k] if k in data else ""
        return out

    def check_password(self, password) -> bool:
        data = self.to_mongo()
        return PassHash.verify(password, data["password"])


class Operator(User):
    created_by = StringField(max_length=500)
    role = ListField(default=["fixer"])  # TODO remove the field
    roles = ListField(default=["fixer"])
    address = StringField(max_length=500)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    city = StringField(max_length=500, required=False)


class Volunteer(Document):
    first_name = StringField(max_length=500, required=True)
    last_name = StringField(max_length=500, required=True)
    phone = IntField(min_value=16, max_value=120)
    email = EmailField(required=True)
    role = ReferenceField(VolunteerRole)
    status = ReferenceField(VolunteerStatus)
    availability_hours_start = IntField(min_value=16, max_value=120)
    availability_hours_end = IntField(min_value=16, max_value=120)
    created_at = DateTimeField(default=dt.now)
    address = StringField(max_length=500, required=True)
    city = StringField(max_length=500, required=False)
    address_old = StringField(max_length=500, required=False)
    is_active = BooleanField(default=False)
    zone_address = StringField(max_length=500, required=True)
    facebook_profile = StringField(max_length=500, required=False)  # URLField(url_regex=FACEBOOK_URL_REGEX)
    age = StringField(max_length=500, required=False)  # IntField(min_value=16, max_value=50)
    # Availability per day in hours
    availability = StringField(
        max_length=500, required=False
    )  # id of type of availability(d2h per daay, 4 hour/week etc)
    availability_day = StringField(max_length=500, required=False)  # when available for the offer_beneficiary_id
    offer_beneficiary_id = StringField(max_length=500, required=False)  # offer_beneficiary_id if ok
    offer_list = ListField(default=[])
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    activity_types = ListField(default=[])  # StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    # created_by = ReferenceField(Operator)
    created_by = StringField(max_length=500)
    team = StringField(max_length=500)
    profession = StringField(max_length=500)
    comments = StringField(max_length=5000)
    offer = StringField(max_length=500)
    timestamp = StringField(max_length=500)
    suburbia = StringField(max_length=500)
    last_temperature = FloatField(min_value=30, max_value=41)
    need_sim_unite = BooleanField(default=False)
    new_volunteer = BooleanField(default=False)
    black_list = BooleanField(default=False)
    received_cards = BooleanField(default=False)
    received_contract = BooleanField(default=False)
    sent_photo = BooleanField(default=False)
    aggreed_terms = BooleanField(default=False)
    april1 = BooleanField(default=False)

class VolunteerRole(Enum):
    delivery = 0,
    copilot = 1,
    packing = 2,
    supply = 3,
    operator = 4


class VolunteerStatus(Enum):
    active = 0,
    inactive = 1,
    blacklistc = 2


class Zone(Enum):
    botanica = 0,
    botanica = 1,
    buiucani = 2,
    centru = 3,
    ciocana = 4,
    riscani = 5,
    telecentru = 6,
    suburbii = 7
