from mongoengine import (
    Document,
    StringField,
    ListField,
    URLField,
    FloatField,
    DateTimeField
)
from datetime import datetime, timezone


class Saree(Document):
    name = StringField(required=True)
    image_urls = ListField(URLField(), default=list)
    variety = StringField()
    remarks = StringField()
    min_price = FloatField(required=True)
    max_price = FloatField(required=True)
    last_edited_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    status = StringField(choices=["published", "unpublished"], default="published")


    def save(self, *args, **kwargs):
        self.last_edited_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "image_urls": self.image_urls,
            "variety": self.variety,
            "remarks": self.remarks,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "status": self.status,
            "last_edited_at": self.last_edited_at.isoformat()
        }
    meta = {"collection": "sarees"}