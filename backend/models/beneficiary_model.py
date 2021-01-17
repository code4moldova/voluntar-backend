from datetime import datetime

from mongoengine import (
    ListField,
    Document,
    IntField,
    StringField,
    DateTimeField,
    BooleanField,
    FloatField,
)

from models.enums import Zone, SpecialCondition
from models.user_model import User


class Beneficiary(Document):
    first_name = StringField(max_length=500)
    last_name = StringField(max_length=500)
    phone = StringField(max_length=8, regex=r"\d")
    landline = StringField(max_length=8, regex=r"\d")
    age = IntField(min_value=16, max_value=120)
    zone = StringField(choices=[zone.name for zone in Zone], required=True)
    address = StringField(max_length=500, required=True)
    apartment = StringField(max_length=10)
    entrance = StringField(max_length=10)
    floor = StringField(max_length=10)

    special_condition = StringField(choices=[sc.value for sc in SpecialCondition], default=None)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    black_list = BooleanField(default=False)

    fixer = StringField(max_length=500)
    created_at = DateTimeField(default=datetime.now())
    created_by = StringField(max_length=500)

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        return data
