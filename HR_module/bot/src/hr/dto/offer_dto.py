from pydantic import BaseModel, ConfigDict, Field


class OfferDto(BaseModel):
    """Данные оффера от БМК-ИТ для отправки кандидату."""

    model_config = ConfigDict(populate_by_name=True)

    offer_id: str = Field(..., alias="offerId")
    telegram_id: str = Field(..., alias="telegramId")
    file_url: str = Field(..., alias="fileUrl")
    file_name: str = Field(default="Offer.pdf", alias="fileName")


class OfferActionDto(BaseModel):
    """Принятие или отклонение оффера."""

    model_config = ConfigDict(populate_by_name=True)

    offer_id: str = Field(..., alias="offerId")
    telegram_id: str = Field(..., alias="telegramId")
