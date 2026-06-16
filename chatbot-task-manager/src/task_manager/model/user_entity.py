from mongoengine import Document, StringField


class UserEntity(Document):
    """
    Entity модель для данных пользователя.

    telegram_id: Идентификатор пользователя в ТГ
    bmk_id: Идентификатор пользователя в БМК-ИТ
    class_id: Идентификатор класса пользователя
    """

    telegram_id = StringField(required=True)
    bmk_id = StringField(required=True)
    class_id = StringField(required=True)
