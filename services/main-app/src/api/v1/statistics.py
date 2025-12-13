from fastapi import APIRouter, Depends

from schemas.statistics import StatisticsResponse
from services.statistics import StatisticsService, get_statistics_service

router = APIRouter()


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    service: StatisticsService = Depends(get_statistics_service),
):
    return await service.get_statistics()

