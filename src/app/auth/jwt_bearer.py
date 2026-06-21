from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Callable, Optional, List
from jose import JWTError
from pydantic import ValidationError
from datetime import datetime, timezone

from app.models.token import TokenPayload
from app.core.config import settings
from app.auth.jwt_handler import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_token_data(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)

        if token_data.sub is None or token_data.exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return token_data

    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _check_expiration(exp: int):
    if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token_data: TokenPayload = Depends(get_token_data)) -> str:
    if token_data.exp is None or token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _check_expiration(token_data.exp)
    return token_data.sub


# -----------------------------
# Role-based dependency factory
# -----------------------------
def require_roles(
    required_roles: Optional[List[str]] = None,
) -> Callable[..., str]:
    required_roles = required_roles or []

    def _dependency(token_data: TokenPayload = Depends(get_token_data)) -> str:
        if token_data.exp is None or token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        _check_expiration(token_data.exp)

        if required_roles:
            user_roles = set(token_data.roles or [])

            if not (user_roles & set(required_roles) or "admin" in user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return token_data.sub

    return _dependency
