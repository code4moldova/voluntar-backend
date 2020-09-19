from enum import Enum

import dt as dt
from mongoengine import ListField, Document, IntField, StringField, ReferenceField, EmailField, DateTimeField, \
    BooleanField, FloatField

from backend.models.user_model import User
from backend.models.volunteer_model import Zone


class Beneficiary(Document):
    first_name = StringField(max_length=500)
    last_name = StringField(max_length=500)
    phone = IntField(min_value=16, max_value=120)
    landline = IntField(min_value=16, max_value=120)
    created_at = DateTimeField(default=dt.now)
    address = StringField(max_length=500, required=True)
    city = StringField(max_length=500, required=False)
    path_receipt = StringField(max_length=500, required=False)
    is_active = BooleanField(default=False)
    zone_address = StringField(max_length=500, required=True)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    offer = StringField(max_length=500)
    age = IntField(min_value=16, max_value=120)
    created_by = StringField(max_length=500)
    have_money = BooleanField(default=True)
    comments = StringField(max_length=5000)
    questions = StringField(max_length=5000)  # ListField(default=[])
    activity_types = ListField(default=[])  # StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    status = StringField(choise=("new", "onProgress", "done", "canceled"), default="new")
    secret = StringField(max_length=500, required=True)
    availability_volunteer = FloatField(min_value=0, max_value=24)
    # beneficiary = ReferenceField(Beneficiary)
    volunteer = StringField(max_length=500)
    fixer = StringField(max_length=500)
    curator = BooleanField(default=False)
    has_symptoms = BooleanField(default=False)
    ask_volunteers = ListField(default=[])
    remarks = ListField(default=[])
    priority = StringField(max_length=100, required=False, default="low")
    urgent = BooleanField(default=False)
    has_disabilities = BooleanField(default=False)
    black_list = BooleanField(default=False)
    group = StringField(max_length=100, default="call_center")
    fixer_comment = StringField(max_length=500, default="")
    additional_info = ListField(default=[])
    suburbia = StringField(max_length=500)
    phone_home = StringField(max_length=500)
    sent_offer = ListField(default=[])
    block = StringField(max_length=500)
    apartament = StringField(max_length=500)
    scara = StringField(max_length=500)
    plata = StringField(max_length=500)


class Beneficiary_request(User):
    have_money = BooleanField(default=True)

class SpecialCondition(Enum):
    disability = 0,
    deaf_mute = 1,
    blind_weak_seer = 2