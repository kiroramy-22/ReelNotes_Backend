from sqlmodel import Field, SQLModel,Column,JSON

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    roles: list[str] = Field(default=["user"], sa_column=Column(JSON))
