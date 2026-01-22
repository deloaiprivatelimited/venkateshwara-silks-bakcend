# models/variety.py

from datetime import datetime
import pytz
from mongoengine import (
    Document, EmbeddedDocument,
    StringField, DateTimeField,
    EmbeddedDocumentField, IntField
)

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)


class AdminMeta(EmbeddedDocument):
    username = StringField(required=True)
    full_name = StringField(required=True)
    last_edited_date = DateTimeField(default=ist_now)


class Variety(Document):
    name = StringField(required=True, unique=True)
    total_saree_count = IntField(default=0)
    admin = EmbeddedDocumentField(AdminMeta)

    meta = {"collection": "varieties"}
