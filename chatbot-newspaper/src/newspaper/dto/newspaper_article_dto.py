from typing import Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, HttpUrl


class NewsArticleDto(BaseModel):
    """
    dto для новости.
    """

    model_config = ConfigDict(populate_by_name=True)

    image_url: Optional[str] = Field(default=None, description="url изображения", alias="imageUrl")
    content: str = Field(..., description="Текст новости")
    source_url: Optional[str] = Field(default=None, description="Ссылка на оригинал новости", alias="sourceUrl")
    message_id: Optional[int] = Field(
        default=None, description="ID сообщения в Telegram", alias="messageId"
    )
    telegram_id: Optional[str] = Field(
        default=None,
        description="ID чата Telegram (ЛС, группа, канал) для отправки",
        alias="telegramId"
    )
