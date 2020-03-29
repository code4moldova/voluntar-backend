import calendar
import json
from datetime import datetime as dt
from mongoengine import (Document, StringField, IntField, EmailField, BooleanField, ListField,
                         DateTimeField, DictField, FloatField, URLField, ReferenceField)
from config import PassHash

FACEBOOK_URL_REGEX = r"http(?:s):\/\/(?:www\.)facebook\.com\/.+"

class User(Document):
    # TODO: Each volunteer must have a reference to operator that was created by
    # created_by = ReferenceField("operator")
    first_name = StringField(max_length=50, default='No_First')
    last_name = StringField(max_length=50, default='No_Last')
    email = EmailField(required=True)
    password = StringField(required=True, min_length=200)
    phone = IntField(min_value=10000000, max_value=99999999)
    created_at = DateTimeField(default=dt.now)
    # we don't delete users just deactivating them
    logins = ListField(default=[])

    is_active = BooleanField(default=True)

    meta = {'allow_inheritance': True}


    def clean_data(self) -> dict:
        data = self.to_mongo()
        if "password" in data and data["password"]:
            del data["password"]
        if "logins" in data:
            del data["logins"]
        return data

    def check_password(self, password) -> bool:
        data = self.to_mongo()
        return PassHash.verify(password, data["password"])


class Operator(User):
    #created_by = ReferenceField(Operator)
    comment = StringField(max_length=500, required=True)

class Volunteer(User):
    address = StringField(max_length=500, required=True)
    telegram_id = StringField(max_length=500, required=False)
    zone_address = StringField(max_length=500, required=True)
    facebook_profile = URLField(url_regex=FACEBOOK_URL_REGEX)
    age = IntField(min_value=16, max_value=50)
    # Availability per day in hours
    availability = FloatField(min_value=0, max_value=12)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    activity_types = StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    #created_by = ReferenceField(Operator)

class Beneficiary(User):
    address = StringField(max_length=500, required=True)
    zone_address = StringField(max_length=500, required=True)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    age = IntField(min_value=16, max_value=50)
    #created_by = ReferenceField(Operator)

class Beneficiary_request(User):
    have_money = BooleanField(default=True)
    comments = StringField(max_length=500, required=True)
    questions = StringField(max_length=500, required=True)
    activity_types = StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    status = StringField(choise=('new', 'onProgress','done','canceled'), default='new')
    availability_volunteer = FloatField(min_value=0, max_value=12)
    #beneficiary = ReferenceField(Beneficiary)
    #volunteer = ReferenceField(Volunteer)
    
