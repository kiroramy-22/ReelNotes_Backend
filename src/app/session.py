from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated

# TODO: Change this to Postgres in prod
# postgres_url = "postgresql+psycopg2://username:password@localhost:5432/dbname"

sqlite_file_name = "database.db"
url = f"sqlite:///{sqlite_file_name}"


engine = create_engine(url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
