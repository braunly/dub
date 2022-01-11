from datetime import datetime

from mongoengine import Document, StringField, BooleanField, DateTimeField
from mongoengine.fields import DictField, IntField, ListField


class User(Document):
    meta = {"indexes": ["#uuid", "#login"]}

    uuid = StringField(required=True, unique=True)
    login = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = StringField(default="example@example.com")
    access = StringField(null=True)
    client = StringField(null=True)
    server = StringField(null=True)
    synthetic = BooleanField(default=False)
    properties = ListField(default=[])

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_player_dict(self):
        data = self.to_mongo().to_dict()
        del data["_id"]
        del data["created_at"]
        del data["updated_at"]

        return data

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