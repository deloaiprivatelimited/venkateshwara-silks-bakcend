from mongoengine import Document, StringField, BooleanField, DateTimeField
from datetime import datetime

class InviteToken(Document):
    token = StringField(required=True, unique=True)
    is_active = BooleanField(default=True)

    # once first device opens link, lock it
    locked_device_id = StringField(default=None)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "invite_tokens"}
