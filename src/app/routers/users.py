from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt_bearer import get_current_user
from app.db.user import UserDB
from app.models.user import User
from sqlmodel import select
from app.session import SessionDep

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=User, operation_id="get_current_user")
async def read_users_me(
    session: SessionDep, current_user: str = Depends(get_current_user)
) -> User:
    """
    Get current user
    """
    user = session.exec(select(UserDB).where(UserDB.id == current_user)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return User.model_validate(user, from_attributes=True)
