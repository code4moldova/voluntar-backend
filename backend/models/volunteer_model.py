from datetime import datetime as dt

from mongoengine import Document, StringField, IntField, EmailField, BooleanField, ListField, DateTimeField, FloatField

from models.enums import VolunteerRole, VolunteerStatus, Zone, WeekDay

FACEBOOK_URL_REGEX = r"http(?:s):\/\/(?:www\.)facebook\.com\/.+"


# Will be deleted after frontend changes
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
        data["_id"] = str(data["_id"])
        return data


class Volunteer(Document):
    first_name = StringField(max_length=500, required=True)
    last_name = StringField(max_length=500, required=True)
    phone = StringField(max_length=8, regex=r"\d")
    email = EmailField(required=True)
    zone = StringField(choices=[zone.name for zone in Zone], required=True)
    address = StringField(max_length=500, required=True)
    age = StringField(max_length=500, required=False)  # IntField(min_value=16, max_value=50)
    facebook_profile = StringField(max_length=500, required=False)  # URLField(url_regex=FACEBOOK_URL_REGEX)
    role = StringField(choices=[vr.value for vr in VolunteerRole])
    availability_hours_start = IntField(min_value=8, max_value=20)  # TODO: Need to discuss the min_value and max_value
    availability_hours_end = IntField(min_value=8, max_value=20)  # TODO: Need to discuss the min_value and max_value
    availability_days = StringField(choices=[weekday.value for weekday in WeekDay])
    status = StringField(choices=[vs.value for vs in VolunteerStatus])
    created_at = DateTimeField(default=dt.now)
    created_by = StringField(max_length=500)  # After frontend changes should be ReferenceField(User)

    # Will be deleted after frontend changes
    city = StringField(max_length=500, required=False)
    address_old = StringField(max_length=500, required=False)
    is_active = BooleanField(default=False)
    zone_address = StringField(max_length=500)
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

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        return data
