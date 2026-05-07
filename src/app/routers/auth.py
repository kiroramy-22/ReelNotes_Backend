from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, status
from jose import JWTError
from pydantic import ValidationError
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.auth.utils import verify_password
from app.session import SessionDep
from app.models.token import Token
from app.core.config import settings
from sqlmodel import select
from app.db.user import UserDB
from app.models.user import LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, operation_id="login_user")
async def login_for_access_token(session: SessionDep, form_data: LoginRequest) -> Token:
    """
    OAuth2 compatible token login, returns an access token
    """
    user = session.exec(
        select(UserDB).where(UserDB.username == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, roles=user.roles, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.email)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token, operation_id="refresh_token")
async def refresh_token(session: SessionDep, refresh_token: str = Body(...)) -> Token:
    """
    Refresh token endpoint
    """
    try:
        payload = decode_token(refresh_token)
        # Verify this is a refresh token
        if "token_type" not in payload or payload["token_type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = session.exec(select(UserDB).where(UserDB.email == email)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=email, roles=user.roles, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(subject=email)
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/sigup", operation_id="signup_user")
async def signup_user(sigup: SignupRequest) -> Token:
    raise NotImplementedError("Signup endpoint is not implemented yet")
