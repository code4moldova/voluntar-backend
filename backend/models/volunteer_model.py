from datetime import datetime as dt

from mongoengine import Document, StringField, IntField, EmailField, BooleanField, ListField, DateTimeField, FloatField

from models.enums import VolunteerRole, VolunteerStatus, Zone, WeekDay

FACEBOOK_URL_REGEX = r"http(?:s):\/\/(?:www\.)facebook\.com\/.+"


class Volunteer(Document):
    first_name = StringField(max_length=500, required=True)
    last_name = StringField(max_length=500, required=True)
    phone = StringField(max_length=8, regex=r"\d")
    email = EmailField(required=True)
    zone = StringField(choices=[zone.name for zone in Zone], required=True)
    address = StringField(max_length=500, required=True)
    age = IntField(min_value=16, max_value=50)
    facebook_profile = StringField(max_length=500, required=False)  # URLField(url_regex=FACEBOOK_URL_REGEX)
    role = ListField(StringField(choices=[vr.value for vr in VolunteerRole]), default=[])
    availability_hours_start = IntField(min_value=8, max_value=22)
    availability_hours_end = IntField(min_value=8, max_value=22)
    availability_days = ListField(StringField(choices=[weekday.name for weekday in WeekDay]), default=[])
    status = StringField(choices=[vs.value for vs in VolunteerStatus], default=VolunteerStatus.active.value)
    created_at = DateTimeField(default=dt.now)
    created_by = StringField(max_length=500)  # After frontend changes should be ReferenceField(User)

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        return data
