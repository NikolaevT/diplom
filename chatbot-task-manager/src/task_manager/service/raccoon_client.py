import httpx

from src.task_manager.config.settings import settings


class RaccoonClient:
    """
    Клиент для взаимодействия с svc-raccoon БМКИТ.
    Получает токен авторизации по логину и паролю.
    """

    def __init__(self) -> None:
        self.base_url = settings.svc_raccoon_url

    async def login(self, login: str, password: str) -> str:
        """
        Получает токен авторизации через svc-raccoon по логину и паролю.
        Args:
            login: Логин пользователя
            password: Пароль пользователя
        Returns:
            Токен авторизации
        """
        url = f"{self.base_url}/v1/login"
        payload = {"login": login, "password": password}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        token = data.get("token")
        if not token:
            raise ValueError("В ответе svc-raccoon отсутствует токен")
        return token

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Обменивает authorization code на токен авторизации через svc-raccoon.
        Args:
            code: Authorization code, полученный от Keycloak
        Returns:
            Токен авторизации
        """
        url = f"{self.base_url}/v1/login/code"
        payload = {"code": code}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        token = data.get("token")
        if not token:
            raise ValueError("В ответе svc-raccoon отсутствует токен")
        return token
