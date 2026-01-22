from mongoengine import (
    Document,
    StringField,
    DateTimeField
)
from datetime import datetime


class AdminUser(Document):
    username = StringField(required=True, unique=True)
    full_name = StringField(required=True)
    password = StringField(required=True)  # no encryption as requested
    date_created = DateTimeField(default=datetime.utcnow)

    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "full_name": self.full_name,
            "date_created": self.date_created.isoformat()
        }
