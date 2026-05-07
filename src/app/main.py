from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routers import users
from app.routers import auth
from app.session import create_db_and_tables

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI JWT Auth Example"}

