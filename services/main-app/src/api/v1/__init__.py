from fastapi import APIRouter

from src.api.v1.comments import router as comments_router
from src.api.v1.task_members import router as task_members_router
from src.api.v1.team_members import router as team_members_router
from src.api.v1.teams import router as teams_router

api_router = APIRouter()
api_router.include_router(comments_router)
api_router.include_router(task_members_router)
api_router.include_router(teams_router)
api_router.include_router(team_members_router)

__all__ = ["api_router"]
