from __future__ import annotations

from fastapi import Header, HTTPException, Request, status
from httpx import Client, HTTPError

from src.targeting_service.config import settings
from src.targeting_service.db import db
from src.targeting_service.repository.distribution_repository import DistributionRepository


def get_distribution_repository(request: Request) -> DistributionRepository:
    return request.app.state.distribution_repository


def ensure_db() -> None:
    """Гарантирует подключение к БД в потоке обработки запроса (Peewee thread-local)."""
    db.connect(reuse_if_open=True)


def ensure_valid_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    """
    Проверка токена через сервис identity.
    Ожидаем заголовок 'Authorization: BAP_Bearer <token>'.
    Если токен невалидный — бросаем HTTP 401 и дальше не идём.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )

    try:
        with Client(timeout=5.0) as client:
            resp = client.get(
                settings.identity_url,
                headers={"Authorization": authorization},
            )
    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity service is unavailable",
        ) from e

    if not resp.is_success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
