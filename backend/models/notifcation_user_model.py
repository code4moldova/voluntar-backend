from datetime import datetime

from mongoengine import Document, ReferenceField, DateTimeField, StringField

from models.notification_model import Notification
from models.user_model import User
from models.enums import NotificationStatus


class NotificationUser(Document):
    user = ReferenceField(User, required=True)
    status = StringField(choices=[status.name for status in NotificationStatus], required=True)
    notification = ReferenceField(Notification, required=True)
    created_at = DateTimeField(default=datetime.utcnow())

    def assign_notification_to_users(self, status="new"):
        users = User.objects().filter(is_active=True)
        for user in users:
            assign_notification = NotificationUser(notification=self, user=user, status=status,)
            assign_notification.save()
