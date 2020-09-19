import dt
from mongoengine import Document, ReferenceField, DateTimeField
from utils.enum import Enum

from backend.models.notification_model import Notification
from backend.models.user_model import User


class NotificationUser(Document):
    user = ReferenceField(User, required=True)
    status = ReferenceField(Notification, required=True)
    created_at = DateTimeField(default=dt.now)


class NotificationStatus(Enum):
    new = 1,
    seen = 2,
    delete = 3
