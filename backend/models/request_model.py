
import dt
from mongoengine import Document, ReferenceField, DateTimeField, StringField, BooleanField
from utils.enum import Enum

from backend.models import Beneficiary
from backend.models.cluster_model import Cluster
from backend.models.user_model import User


class RequestStatus(Document, Enum):
    new = [1]
    confirmed = 2,
    in_process = 3,
    canceled = 4,
    solved = 5,
    archived = 6


class Request(Document):
    beneficiary = ReferenceField(Beneficiary, required=True)
    user = ReferenceField(User, required=True)
    status = ReferenceField(RequestStatus, required=True)
    secret = StringField(max_length=100)
    urgent = BooleanField(default=False)
    comments = StringField(max_length=1000)
    has_symptoms = BooleanField(default=False)
    cluster = ReferenceField(Cluster)
    created_at = DateTimeField(default=dt.now)