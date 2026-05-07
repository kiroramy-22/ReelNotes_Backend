from sqlmodel import Field, SQLModel, Column, JSON
import uuid


class UserDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str
    email: str
    password: str
    roles: list[str] = Field(default=["user"], sa_column=Column(JSON))
