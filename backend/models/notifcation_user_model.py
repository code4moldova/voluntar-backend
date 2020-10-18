from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField, StringField

from models.notification_model import Notification
from models.user_model import User
from models.enums import NotificationStatus


class NotificationUser(Document):
    user = ReferenceField(User, required=True)
    status = StringField(choices=[status.name for status in NotificationStatus], required=True)
    notification = ReferenceField(Notification, required=True)
    created_at = DateTimeField(default=datetime.now())
