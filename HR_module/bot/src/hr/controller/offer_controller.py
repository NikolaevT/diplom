from fastapi import APIRouter

from src.hr.dto import OfferDto
from src.hr.service.offer_service import notify_offer

router = APIRouter(
    prefix="/api/v1/offers",
    tags=["offers"],
)


@router.post("")
async def receive_offer(offer: OfferDto):
    """Принимает оффер от БМК-ИТ и отправляет его кандидату в Telegram."""
    return await notify_offer(offer)
