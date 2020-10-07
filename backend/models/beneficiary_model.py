from datetime import datetime

from mongoengine import (
    ListField,
    Document,
    IntField,
    StringField,
    ReferenceField,
    DateTimeField,
    BooleanField,
    FloatField,
)

from models.enums import Zone, SpecialCondition
from models.user_model import User


class Beneficiary(Document):
    first_name = StringField(max_length=500)
    last_name = StringField(max_length=500)
    phone = StringField(max_length=8, regex=r'\d')
    landline = IntField(min_value=16, max_value=120)
    age = IntField(min_value=16, max_value=120)
    zone = StringField(choices=[zone.value for zone in Zone], required=True)
    address = StringField(max_length=500, required=True)
    special_condition = StringField(choices=[sc.value for sc in SpecialCondition], default="")
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    created_at = DateTimeField(default=datetime.now())
    created_by = StringField(max_length=500)

    # Will be deleted after frontend changes
    path_receipt = StringField(max_length=500, required=False)
    is_active = BooleanField(default=False)
    zone_address = StringField(max_length=500, required=True)
    offer = StringField(max_length=500)
    city = StringField(max_length=500, required=False)
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
