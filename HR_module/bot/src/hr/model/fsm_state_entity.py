from mongoengine import Document, DynamicField, IntField, StringField


class FSMStateEntity(Document):
    """
    Entity для хранения FSM состояний Telegram-пользователя.
    """

    user_id = IntField(required=True)
    chat_id = IntField(required=True)
    state = StringField(default=None)
    data = DynamicField(default=dict)

    meta = {
        "collection": "fsm_states",
        "indexes": [
            {"fields": ["user_id", "chat_id"], "unique": True},
        ],
    }
