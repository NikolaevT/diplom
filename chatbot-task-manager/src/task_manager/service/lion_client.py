from typing import Any, Dict

import httpx

from src.task_manager.config.settings import settings


class LionClient:
    """
    Клиент для взаимодействия с svc-lion БМКИТ.
    Получает данные пользователя (id, classId) из /v1/identity.
    """

    def __init__(self) -> None:
        self.base_url = settings.svc_lion_url

    async def get_identity(self, token: str) -> Dict[str, Any]:
        """
        Получает данные пользователя из svc-lion/v1/identity.
        Args:
            token: Токен авторизации (полученный от svc-raccoon)
        Returns:
            Словарь с данными пользователя, включая 'id' и 'classId'
        """
        url = f"{self.base_url}/v1/identity"
        headers = {"Authorization": f"BAP_Bearer {token}"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data
