from mongoengine import (
    Document,
    StringField,
    ListField,
    URLField,
    FloatField,
    DateTimeField,
    IntField,
)
from datetime import datetime, timezone


# ✅ Counter collection
class Counter(Document):
    name = StringField(required=True, unique=True)
    seq = IntField(default=0)
    meta = {"collection": "counters"}


def get_next_saree_number():
    counter = Counter.objects(name="saree").modify(
        upsert=True,
        new=True,
        inc__seq=1
    )
    return counter.seq


class Saree(Document):
    name = StringField(required=False)   # ✅ optional (auto generated)
    image_urls = ListField(URLField(), default=list)
    variety = StringField()
    remarks = StringField()
    min_price = FloatField(required=True)
    max_price = FloatField(required=True)
    last_edited_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    status = StringField(choices=["published", "unpublished"], default="published")

    meta = {"collection": "sarees"}

    def save(self, *args, **kwargs):
        # ✅ auto name
        if not self.name:
            num = get_next_saree_number()
            self.name = f"Saree{num:03d}"

        self.last_edited_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

   def to_json(self):
    cloudfront_domain = "https://d34wwgjscxms4y.cloudfront.net"

    updated_image_urls = []
    for url in self.image_urls:
        # If already full URL, replace domain
        if url.startswith("http"):
            # Extract file path after last '/'
            file_path = url.split(".com/")[-1] if ".com/" in url else url.split("/")[-1]
            updated_image_urls.append(f"{cloudfront_domain}/{file_path}")
        else:
            # If stored as relative path
            updated_image_urls.append(f"{cloudfront_domain}/{url}")

    return {
        "id": str(self.id),
        "name": self.name,
        "image_urls": updated_image_urls,
        "variety": self.variety,
        "remarks": self.remarks,
        "min_price": self.min_price,
        "max_price": self.max_price,
        "status": self.status,
        "last_edited_at": self.last_edited_at.isoformat()
    }
