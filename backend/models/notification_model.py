from datetime import datetime, timezone

from mongoengine import Document, ReferenceField, DateTimeField, StringField

from models.enums import NotificationType
from models.request_model import Request


class Notification(Document):
    type = StringField(choices=[type.name for type in NotificationType], required=True)
    subject = StringField(max_length=100)
    request = ReferenceField(Request, required=True)
    created_at = DateTimeField(default=datetime.now())

    def clean_data(self) -> dict:
        data = self.to_mongo()
        data["_id"] = str(data["_id"])
        data["request"] = str(data["request"])
        return data
