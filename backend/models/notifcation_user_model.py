from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField

from models.notification_model import Notification
from models.user_model import User


class NotificationUser(Document):
    user = ReferenceField(User, required=True)
    status = ReferenceField(Notification, required=True)
    created_at = DateTimeField(default=datetime.now())
