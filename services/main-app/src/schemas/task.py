from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from enums.task_status import TaskStatus


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: datetime | None = None
    user_id: UUID
    column_id: UUID


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None
    column_id: UUID | None = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    due_date: datetime | None
    user_id: UUID
    column_id: UUID
    created_at: datetime
    updated_at: datetime
