from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.v1.auth import router as auth_router
from api.v1.boards import router as boards_router
from api.v1.columns import router as columns_router
from api.v1.statistics import router as statistics_router
from api.v1.tasks import router as tasks_router
from api.v1.team_members import router as team_members_router
from api.v1.teams import router as teams_router
from core.config import settings
from exceptions import InvalidCredentialsError

app = FastAPI(
    title=settings.app_settings.app_name,
    version=settings.app_settings.app_version,
)


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


app.include_router(teams_router, prefix="/api/v1")
app.include_router(team_members_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(boards_router, prefix="/api/v1")
app.include_router(columns_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Main App is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "main-app"}
