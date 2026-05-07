from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None


class User(UserBase):
    id: str
    username: str
    roles: List[str] = ["user"]
