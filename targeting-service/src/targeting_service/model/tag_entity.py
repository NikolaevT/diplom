from datetime import datetime
from uuid import uuid4

from peewee import UUIDField, TextField, DateTimeField, CharField

from src.targeting_service.db import BaseModel


class TagEntity(BaseModel):
    """
    модель тэга
    """

    id = UUIDField(primary_key=True, default=uuid4)
    name = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = CharField(null=True)
    updated_by = CharField(null=True)

    class Meta:
        table_name = "tag"
