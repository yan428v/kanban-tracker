from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateTaskMemberRequest(BaseModel):
    task_id: UUID
    user_id: UUID


class TaskMemberResponse(BaseModel):
    id: UUID
    task_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
