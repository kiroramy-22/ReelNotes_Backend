from fastapi import FastAPI
from app.core.config import settings
from app.routers import users
from app.routers import auth
from app.session import create_db_and_tables

DDDDD = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
@DDDDD.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include routers
DDDDD.include_router(auth.router)
DDDDD.include_router(users.router, prefix=settings.API_V1_STR)
@DDDDD.get("/")
async def root():
    return {"message": "Welcome to FastAPI JWT Auth Example"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)