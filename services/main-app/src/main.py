from fastapi import FastAPI

from api.v1.statistics import router as statistics_router
from api.v1.team_members import router as team_members_router
from api.v1.teams import router as teams_router
from core.config import settings

app = FastAPI(
    title=settings.app_settings.app_name,
    version=settings.app_settings.app_version,
)

app.include_router(teams_router, prefix="/api/v1")
app.include_router(team_members_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Main App is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "main-app"}
