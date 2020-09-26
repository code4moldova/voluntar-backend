from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField

from models.volunteer_model import Volunteer


class Cluster(Document):
    volunteer = ReferenceField(Volunteer, required=True)
    created_at = DateTimeField(default=datetime.now())
