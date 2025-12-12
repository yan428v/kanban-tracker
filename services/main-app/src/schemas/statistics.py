from uuid import UUID

from pydantic import BaseModel


class EntityCountsResponse(BaseModel):
    teams: int
    users: int
    boards: int
    tasks: int
    comments: int


class TasksByAssigneeResponse(BaseModel):
    user_id: UUID
    count: int


class WorkDistributionResponse(BaseModel):
    tasks_per_status: dict[str, int]
    tasks_by_assignee: list[TasksByAssigneeResponse]


class DueDateHealthResponse(BaseModel):
    overdue_count: int
    due_soon_count: int
    missing_due_date_count: int


class StatisticsResponse(BaseModel):
    entity_counts: EntityCountsResponse
    work_distribution: WorkDistributionResponse
    due_date_health: DueDateHealthResponse
