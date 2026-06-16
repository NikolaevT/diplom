"""
Модель новости (News Article Entity).
"""

from typing import Optional

from mongoengine import BinaryField, Document, StringField


class NewsArticleEntity(Document):
    """
    Entity модель для новости.
    """

    image_bytes: Optional[bytes] = BinaryField()
    content: str = StringField(required=True)
    source_url: Optional[str] = StringField()
    telegram_id: Optional[str] = StringField()
