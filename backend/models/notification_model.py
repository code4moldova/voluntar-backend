from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField, StringField

from models.enums import NotificationType
from models.request_model import Request


class Notification(Document):
    type = ReferenceField(NotificationType, required=True)
    subject = StringField(max_length=100)
    request = ReferenceField(Request, required=True)
    created_at = DateTimeField(default=datetime.now())
