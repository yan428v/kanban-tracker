from fastapi import Depends

from repositories.statistics import (
    StatisticsRepository,
    get_statistics_repository,
)
from schemas.statistics import (
    CompletedHistoryPoint,
    DueDateHealthResponse,
    EntityCountsResponse,
    StatisticsResponse,
    TasksByAssigneeResponse,
    WorkDistributionResponse,
)


class StatisticsService:
    def __init__(self, repository: StatisticsRepository):
        self.repository = repository

    async def get_statistics(self) -> StatisticsResponse:
        entity_counts_data = await self.repository.get_entity_counts()
        tasks_by_status = await self.repository.get_tasks_by_status()
        tasks_by_assignee_data = await self.repository.get_tasks_by_assignee()
        due_date_health_data = await self.repository.get_due_date_health()
        completed_history_data = await self.repository.get_completed_history()

        entity_counts = EntityCountsResponse(**entity_counts_data)

        tasks_by_assignee = [
            TasksByAssigneeResponse(**item) for item in tasks_by_assignee_data
        ]

        work_distribution = WorkDistributionResponse(
            tasks_per_status=tasks_by_status,
            tasks_by_assignee=tasks_by_assignee,
        )

        due_date_health = DueDateHealthResponse(**due_date_health_data)

        completed_history = [
            CompletedHistoryPoint(**item) for item in completed_history_data
        ]

        return StatisticsResponse(
            entity_counts=entity_counts,
            work_distribution=work_distribution,
            due_date_health=due_date_health,
            completed_history=completed_history,
        )


async def get_statistics_service(
    repository: StatisticsRepository = Depends(get_statistics_repository),
) -> StatisticsService:
    return StatisticsService(repository)

