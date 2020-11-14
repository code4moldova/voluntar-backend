from datetime import datetime

from mongoengine import Document, IntField, ReferenceField, DateTimeField, StringField, BooleanField

from models.beneficiary_model import Beneficiary
from models.cluster_model import Cluster
from models.enums import RequestStatus, RequestType
from models.user_model import User


class Request(Document):
    beneficiary = ReferenceField(Beneficiary, required=True)
    user = ReferenceField(User, required=True)
    type = StringField(choices=[item.name for item in RequestType], required=True)
    status = StringField(choices=[item.name for item in RequestStatus], required=True)
    number = IntField()
    secret = StringField(max_length=100)
    urgent = BooleanField(default=False)
    comments = StringField(max_length=1000)
    has_symptoms = BooleanField(default=False)
    cluster = ReferenceField(Cluster)
    created_at = DateTimeField(default=datetime.now())

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        data["beneficiary"] = str(data["beneficiary"])
        data["user"] = str(data["user"])

        return data
