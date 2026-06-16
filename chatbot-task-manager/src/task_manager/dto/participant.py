from typing import List

from pydantic import BaseModel, Field


class Participant(BaseModel):
    """Участник чата"""

    user_id: int = 0
    name: str = ""


class Participants(BaseModel):
    participants: List[Participant] = Field(default_factory=list)
