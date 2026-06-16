from peewee import UUIDField, CharField, BooleanField, ForeignKeyField, CompositeKey, Model, PostgresqlDatabase
import uuid
from src.targeting_service.config import settings


db = PostgresqlDatabase(
    settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)


class BaseModel(Model):
    class Meta:
        database = db

class Recipient(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    telegram_id = CharField(unique=True)
    name = CharField(null=True)
    type = CharField()
    is_admin = BooleanField(default=False)

    class Meta:
        table_name = 'recipient'

class Tag(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(unique=True)
    
    class Meta:
        table_name = 'tag'

class Distribution(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    bmc_distribution_id = CharField(unique=True)
    name = CharField(null=True)
    
    class Meta:
        table_name = 'distribution'

class DistributionTag(BaseModel):
    distribution_id = ForeignKeyField(Distribution)
    tag_id = ForeignKeyField(Tag)
    
    class Meta:
        table_name = 'distribution_tag'
        primary_key = CompositeKey('distribution_id', 'tag_id')

class RecipientTag(BaseModel):
    recipient_id = ForeignKeyField(Recipient)
    tag_id = ForeignKeyField(Tag)
    
    class Meta:
        table_name = 'recipient_tag'
        primary_key = CompositeKey('recipient_id', 'tag_id')
