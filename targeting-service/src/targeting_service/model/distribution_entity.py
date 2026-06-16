from datetime import datetime
from uuid import uuid4

from peewee import CharField, DateTimeField, TextField, UUIDField

from src.targeting_service.db import BaseModel


class DistributionEntity(BaseModel):
    """
    модель рассылки.
    """

    id = UUIDField(primary_key=True, default=uuid4)
    bmc_distribution_id = CharField(unique=True)
    name = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = CharField(null=True)
    updated_by = CharField(null=True)

    class Meta:
        table_name = "distribution"
