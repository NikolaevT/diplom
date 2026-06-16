import base64
import json
import time

from fastapi import Header, HTTPException, Security, status
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger

from src.newspaper.security.auth_scheme import BAPBearer


def _decode_jwt_payload(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT format",
        )

    payload_b64 = parts[1]
    padding = "=" * (-len(payload_b64) % 4)

    try:
        decoded_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(decoded_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot decode JWT payload",
        ) from exc


async def require_jwt(
    token: str | None = Security(BAPBearer(auto_error=True)),
    authorization: str | None = Header(default=None),
):
    """
    Минимальная проверка JWT: наличие заголовка, формат Bearer, exp не истёк.
    Подпись пока не проверяем.
    """
    scheme: str | None = None

    # Если токен пришёл через кастомную схему (Swagger / Security), считаем префикс BAP_Bearer
    if token:
        scheme = "BAP_Bearer"

    # Если не пришёл (auto_error=False), пробуем разобрать обычный Authorization
    if not token and authorization:
        parsed_scheme, parsed_token = get_authorization_scheme_param(authorization)
        scheme = parsed_scheme.strip() if parsed_scheme else None
        if scheme and scheme.lower() in ("bap_bearer", "bearer"):
            token = parsed_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    if scheme and scheme not in ("Bearer", "BAP_Bearer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be Bearer",
        )

    payload = _decode_jwt_payload(token)
    exp = payload.get("exp")
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT exp claim is missing",
        )

    now = int(time.time())
    if exp < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token expired",
        )

    logger.info(f"JWT token valid until {exp}")
    return payload
