from fastapi import FastAPI
from core.config import settings

app = FastAPI(
    title=settings.app_settings.app_name,
    version=settings.app_settings.app_version,
)

@app.get("/")
async def root():
    return {"message": "Main App is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "main-app"}