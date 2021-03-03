from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField

from models.volunteer_model import Volunteer


class Cluster(Document):
    """This is like a batch of Requests that volunteer can take in single delivery"""

    volunteer = ReferenceField(Volunteer, required=True)
    created_at = DateTimeField(default=datetime.utcnow())

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        data["volunteer"] = str(data["volunteer"])
        return data
