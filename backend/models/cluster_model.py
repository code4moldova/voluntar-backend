import dt
from mongoengine import Document, ReferenceField, DateTimeField

from backend.models import Volunteer


class Cluster(Document):
    volunteer = ReferenceField(Volunteer, required=True)
    created_at = DateTimeField(default=dt.now)
