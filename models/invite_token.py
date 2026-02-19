from mongoengine import Document, StringField, BooleanField, DateTimeField,ReferenceField
from datetime import datetime
from models.category import Category
class InviteToken(Document):
    token = StringField(required=True, unique=True)
    is_active = BooleanField(default=True)

    # once first device opens link, lock it
    locked_device_id = StringField(default=None)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "invite_tokens"}


class CategoryInviteToken(Document):
    token = StringField(required=True, unique=True)
    category = ReferenceField(Category, required=True)
    is_active = BooleanField(default=True)
    locked_device_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "category_invite_tokens",
        "indexes": ["token", "category"]
    }
