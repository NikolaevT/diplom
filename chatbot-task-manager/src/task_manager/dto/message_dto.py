from pydantic import BaseModel


class Message(BaseModel):
    """Сообщение"""

    user_id: int = 0
    chat_id: int = 0
    text: str = ""
    time: str = ""
