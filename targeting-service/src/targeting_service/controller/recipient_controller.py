from fastapi import APIRouter, Depends

from src.targeting_service.deps import ensure_db
from src.targeting_service.dto.recipient_dto import RecipientDto
from src.targeting_service.service.recipient_service import create_or_update_recipient


router = APIRouter(prefix="/api/v1/recipients", tags=["bot-recipients"])


@router.post(
    "",
    response_model=RecipientDto,
    summary="Создать получателя Telegram",
    description=("Регистрирует нового получателя по telegram_id."),
)
def create_recipient_endpoint(
    payload: RecipientDto,
    _: None = Depends(ensure_db),
) -> RecipientDto:
    return create_or_update_recipient(payload)
