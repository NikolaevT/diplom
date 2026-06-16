from typing import Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict



class DistributionListDto(BaseModel):
    """DTO для списка рассылок (без поста)."""

    model_config = ConfigDict(populate_by_name=True)

    bmc_distribution_id: str = Field(..., description="ID рассылки", alias="bmcDistributionId")
    name: Optional[str] = Field(description="Наименование группы, чата, канала")


class BotNewsRequest(BaseModel):
    """Тело POST в /api/v1/news бота."""

    model_config = ConfigDict(populate_by_name=True)

    
    image_url: Optional[str] = Field(None, alias="imageUrl")
    content: str = Field(..., description="Текст поста")
    source_url: Optional[str] = Field(None, alias="sourceUrl")
    telegram_id: str = Field(
        ..., alias="telegramId", description="ID чата Telegram (ЛС, группа, канал) для отправки"
    )


class PostDto(BaseModel):
    """DTO для поста."""

    model_config = ConfigDict(populate_by_name=True)

    image_url: Optional[str] = Field(default=None, description="Содержимое поста", alias="imageUrl")
    
    content: str = Field(..., description="Содержимое поста")
    
    source_url: Optional[str] = Field(default=None, description="URL источника поста", alias="sourceUrl")


class DistributionDto(BaseModel):
    """
    DTO для рассылки
    """

    model_config = ConfigDict(populate_by_name=True)

    bmc_distribution_id: str = Field(
        ..., description="Ключ группы/чата/канала из БМК ИТ", alias="bmcDistributionId"
    )
    name: str = Field(..., description="Наименование группы, чата, канала")
    post: PostDto = Field(..., description="Пост")


class DistributionUpdate(BaseModel):
    """DTO для обновления рассылки"""

    name: str = Field(..., description="Наименование группы, чата, канала")
