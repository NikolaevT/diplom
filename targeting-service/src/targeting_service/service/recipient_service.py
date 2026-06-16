from src.targeting_service.db import db
from src.targeting_service.dto.recipient_dto import RecipientDto
from src.targeting_service.mapper.recipient_mapper import RecipientMapper
from src.targeting_service.repository import recipient_repository


def create_or_update_recipient(dto: RecipientDto) -> RecipientDto:
    """
    Получаем DTO получателя, конвертируем в Entity, сохраняем в БД.
    Если получатель уже есть по telegram_id — обновляем, иначе создаём.
    """
    with db.atomic():
        # В DTO поля приходят в camelCase (telegramId, isAdmin),
        # а в Entity/БД используются snake_case (telegram_id, is_admin).
        existing = recipient_repository.find_by_telegram_id(dto.telegram_id)

        if existing is not None:
            # обновляем существующую entity из dto
            existing.name = dto.name
            existing.type = dto.type
            existing.is_admin = dto.is_admin
            saved = recipient_repository.update(existing)
        else:
            # создаём новую entity через маппер
            entity = RecipientMapper.to_entity(dto)
            saved = recipient_repository.create(entity)

    return RecipientMapper.to_dto(saved)
