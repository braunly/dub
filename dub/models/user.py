from datetime import datetime

from mongoengine import Document, StringField, BooleanField, DateTimeField
from mongoengine.fields import ListField


class User(Document):
    meta = {"indexes": ["#uuid", "#login"]}

    uuid = StringField(required=True, unique=True)
    login = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = StringField(default="empty@example.com")
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
        if '_id' in data: del data["_id"]
        if 'created_at' in data: del data["created_at"]
        if 'updated_at' in data: del data["updated_at"]

        return data

