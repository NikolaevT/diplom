from datetime import datetime

from mongoengine import DateTimeField, Document, IntField, StringField


class MessageEntity(Document):
    """
    Entity модель для сообщений.

    chat_id: Идентификатор чата
    user_id: Идентификатор юзера
    content: Текст сообщения
    created_at: Дата и время отправки сообщения
    """

    chat_id: int = IntField(required=True)
    user_id: str = StringField(required=True)
    content: str = StringField(required=True)
    created_at: datetime = DateTimeField(required=True)
