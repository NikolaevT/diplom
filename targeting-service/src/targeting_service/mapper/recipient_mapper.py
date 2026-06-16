from src.targeting_service.dto.recipient_dto import RecipientDto
from src.targeting_service.model.recipient_entity import RecipientEntity


class RecipientMapper:
    """
    Маппер для преобразования Recipient DTO <-> RecipientEntity.

    """

    @staticmethod
    def to_entity(dto: RecipientDto) -> RecipientEntity:
        return RecipientEntity(
            telegram_id=dto.telegram_id,
            name=dto.name,
            type=dto.type,
            is_admin=dto.is_admin,
        )

    @staticmethod
    def to_dto(entity: RecipientEntity) -> RecipientDto:
        return RecipientDto(
            telegram_id=entity.telegram_id,
            name=entity.name,
            type=entity.type,
            is_admin=entity.is_admin,
        )
