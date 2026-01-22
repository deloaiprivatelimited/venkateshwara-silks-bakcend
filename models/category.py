from datetime import datetime
import pytz
from mongoengine import (
    Document, EmbeddedDocument,
    StringField, DateTimeField,
    EmbeddedDocumentField, ListField, ReferenceField
)
from models.saree import Saree

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)


class AdminMeta(EmbeddedDocument):
    username = StringField(required=True)
    full_name = StringField(required=True)
    last_edited_date = DateTimeField(default=ist_now)


class Category(Document):
    name = StringField(required=True, unique=True)
    sarees = ListField(ReferenceField(Saree, reverse_delete_rule=2))  # CASCADE
    admin = EmbeddedDocumentField(AdminMeta)

    meta = {
        "collection": "categories",
        "indexes": ["name"]
    }
