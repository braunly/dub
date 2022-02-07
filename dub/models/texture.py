from datetime import datetime

from mongoengine import Document, StringField, BooleanField, DateTimeField
from mongoengine.fields import DictField, IntField

class Texture(Document):
    meta = {"indexes": ["kind", "deleted", "-created"]}

    token = StringField(required=True)
    created = DateTimeField(default=datetime.utcnow)
    kind = StringField(max_length=6, required=True)
    deleted = BooleanField(default=False)
    metadata = DictField(default=dict)

    height = IntField(null=True)
    width = IntField(null=True)
    image = StringField(null=True)