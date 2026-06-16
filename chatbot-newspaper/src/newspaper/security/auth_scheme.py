from fastapi import HTTPException, Request, status
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param


class BAPBearer(SecurityBase):
    """
    Кастомная схема авторизации бмк: заголовок Authorization: BAP_Bearer <token>.
    """

    def __init__(
        self,
        scheme_name: str = "BAP_Bearer",
        description: str = "BAP Bearer token authentication",
        auto_error: bool = True,
    ):
        self.scheme_name = scheme_name
        self.auto_error = auto_error
        self.model = HTTPBearerModel(scheme="bearer", bearerFormat="JWT", description=description)

    async def __call__(self, request: Request) -> str | None:
        authorization: str | None = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header is missing",
                    headers={"WWW-Authenticate": "BAP_Bearer"},
                )
            return None

        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bap_bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "BAP_Bearer"},
                )
            return None

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT token is empty",
                    headers={"WWW-Authenticate": "BAP_Bearer"},
                )
            return None

        return token
