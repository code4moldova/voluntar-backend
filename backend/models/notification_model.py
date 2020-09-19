
import dt
from mongoengine import Document, ReferenceField, DateTimeField, StringField
from utils.enum import Enum

from backend.models.user_model import User


class NotificationType(Enum):
    new_request = 1,
    canceled_request = 2


class Notification(Document):
    type = ReferenceField(NotificationType, required=True)
    subject = StringField(max_length=100)
    request = ReferenceField(Request, required=True)
    created_at = DateTimeField(default=dt.now)
