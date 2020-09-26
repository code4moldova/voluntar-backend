from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField, StringField, BooleanField

from models.beneficiary_model import Beneficiary
from models.cluster_model import Cluster
from models.enums import RequestStatus
from models.user_model import User


class Request(Document):
    beneficiary = ReferenceField(Beneficiary, required=True)
    user = ReferenceField(User, required=True)
    status = ReferenceField(RequestStatus, required=True)
    secret = StringField(max_length=100)
    urgent = BooleanField(default=False)
    comments = StringField(max_length=1000)
    has_symptoms = BooleanField(default=False)
    cluster = ReferenceField(Cluster)
    created_at = DateTimeField(default=datetime.now())
