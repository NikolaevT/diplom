from datetime import datetime
from uuid import uuid4

from peewee import BooleanField, CharField, DateTimeField, TextField, UUIDField

from src.targeting_service.db import BaseModel


class RecipientEntity(BaseModel):
    """
    модель получателя.
    """

    id = UUIDField(primary_key=True, default=uuid4)
    telegram_id = CharField(unique=True)
    name = TextField(null=True)
    type = TextField()
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = CharField(null=True)
    updated_by = CharField(null=True)

    class Meta:
        table_name = "recipient"
