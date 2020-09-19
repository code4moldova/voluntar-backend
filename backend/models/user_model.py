from enum import Enum

import dt as dt
from mongoengine import ListField, Document, IntField, StringField, ReferenceField, EmailField, DateTimeField, \
    BooleanField

from backend.models.volunteer_model import Zone


class User(Document):
    # TODO: Each volunteer must have a reference to operator that was created by
    # created_by = ReferenceField("operator")
    role = ListField(default=[])
    availability_hours_start = IntField(min_value=10000000, max_value=99999999)
    availability_hours_end = IntField(min_value=10000000, max_value=99999999)
    availability_days = ListField(default=[])
    address = StringField(required=True, min_length=4)
    zone = ReferenceField(Zone,required=True)
    first_name = StringField(max_length=50, default="No_First")
    last_name = StringField(max_length=50, default="No_Last")
    email = EmailField(required=True)
    password = StringField(required=True, min_length=6)
    phone = IntField(min_value=10000000, max_value=99999999)
    created_at = DateTimeField(default=dt.now)
    last_access = DateTimeField(default=dt.now)
    # we don't delete users just deactivating them
    logins = ListField(default=[])
    is_active = BooleanField(default=True)

    meta = {"allow_inheritance": True}

    class Role(Enum):
        administrator = 0,
        coordinator = 1,
        operator = 2

    class WeekDay(Enum):
        monday = 0,
        tuesday = 1,
        wednesday = 2,
        thursday = 3,
        friday = 4,
        saturday = 5,
        sunday = 6
