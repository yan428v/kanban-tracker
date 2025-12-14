from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models import User
from schemas.statistics import StatisticsResponse
from services.statistics import StatisticsService, get_statistics_service

router = APIRouter()


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_statistics()
