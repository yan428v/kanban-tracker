from fastapi import FastAPI
from core.config import settings
from api.v1.teams import router as teams_router

app = FastAPI(
    title=settings.app_settings.app_name,
    version=settings.app_settings.app_version,
)

app.include_router(teams_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Main App is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "main-app"}