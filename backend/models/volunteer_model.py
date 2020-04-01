import calendar
import json
from datetime import datetime as dt
from mongoengine import (Document, StringField, IntField, EmailField, BooleanField, ListField,
                         DateTimeField, DictField, FloatField, URLField, ReferenceField)
from config import PassHash

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

FACEBOOK_URL_REGEX = r"http(?:s):\/\/(?:www\.)facebook\.com\/.+"

class User(Document):
    # TODO: Each volunteer must have a reference to operator that was created by
    # created_by = ReferenceField("operator")
    first_name = StringField(max_length=50, default='No_First')
    last_name = StringField(max_length=50, default='No_Last')
    email = EmailField(required=True)
    password = StringField(required=True, min_length=6)
    phone = IntField(min_value=10000000, max_value=99999999)
    created_at = DateTimeField(default=dt.now)
    last_access = DateTimeField(default=dt.now)
    # we don't delete users just deactivating them
    logins = ListField(default=[])

    is_active = BooleanField(default=True)

    meta = {'allow_inheritance': True}

    def generate_auth_token(self, expiration = 60000):
        secret = 'lalal'#app.config['SECRET_KEY']
        s = Serializer(secret, expires_in = expiration)
        User.objects(id=str(self.id)).get().update(last_access=dt.now)
        obj = self.clean_data()
        for k in obj.keys():
            if type(obj[k]) is dt:
                del obj[k]
        return s.dumps(obj)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('lalal')#app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.objects(id=data['id'])
        return user

    def clean_data(self) -> dict:
        data = self.to_mongo()
        if "password" in data and data["password"]:
            del data["password"]
        if "logins" in data:
            del data["logins"]
        data['_id'] = str(data['_id'])
        return data

    def check_password(self, password) -> bool:
        data = self.to_mongo()
        return PassHash.verify(password, data["password"])

class Operator(User):
    created_by = StringField(max_length=500)
    role =ListField(default=['fixer'])# StringField(choise=('operator', 'fixer'), default='fixer')
    address = StringField(max_length=500)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)

class Volunteer(User):
    address = StringField(max_length=500, required=True)
    telegram_id = StringField(max_length=500, required=False)
    zone_address = StringField(max_length=500, required=True)
    facebook_profile = StringField(max_length=500, required=False)#URLField(url_regex=FACEBOOK_URL_REGEX)
    age = IntField(min_value=16, max_value=50)
    # Availability per day in hours
    availability = FloatField(min_value=0, max_value=12)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    activity_types = StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    #created_by = ReferenceField(Operator)
    created_by = StringField(max_length=500)
    team = StringField(max_length=500)
    profesia = StringField(max_length=500)
    comments = StringField(max_length=500)
    last_tempreture = FloatField(min_value=36, max_value=41)
    need_sim_unite = BooleanField(default=False)
    new_volunteer = BooleanField(default=True)
    black_list = BooleanField(default=False)
    received_cards = BooleanField(default=False)
    sent_photo = BooleanField(default=False)


class Beneficiary(User):
    address = StringField(max_length=500, required=True)
    zone_address = StringField(max_length=500, required=True)
    latitude = FloatField(min_value=0, max_value=50)
    longitude = FloatField(min_value=0, max_value=50)
    age = IntField(min_value=16, max_value=50)
    created_by = StringField(max_length=500)
    have_money = BooleanField(default=True)
    comments = StringField(max_length=500, required=True)
    questions = StringField(max_length=500, required=True)
    activity_types = StringField(choise=('Activity0', 'Activity1'), default='Activity0')
    status = StringField(choise=('new', 'onProgress','done','canceled'), default='new')
    secret = StringField(max_length=500, required=True)
    availability_volunteer = FloatField(min_value=0, max_value=12)
    #beneficiary = ReferenceField(Beneficiary)
    volunteer = StringField(max_length=500)
    fixer = StringField(max_length=500)
    

class Beneficiary_request(User):
    have_money = BooleanField(default=True)

