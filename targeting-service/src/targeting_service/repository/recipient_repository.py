from datetime import datetime
from typing import Optional

from src.targeting_service.model.recipient_entity import RecipientEntity


def create(entity: RecipientEntity) -> RecipientEntity:
    entity.save(force_insert=True)
    return entity


def update(entity: RecipientEntity) -> RecipientEntity:
    entity.updated_at = datetime.utcnow()
    entity.save()
    return entity


def find_by_telegram_id(telegram_id: str) -> Optional[RecipientEntity]:
    return RecipientEntity.get_or_none(RecipientEntity.telegram_id == telegram_id)


def delete_by_telegram_id(telegram_id: str) -> None:
    (RecipientEntity.delete().where(RecipientEntity.telegram_id == telegram_id).execute())
