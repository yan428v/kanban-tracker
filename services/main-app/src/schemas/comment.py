from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    body: str


class CommentCreate(CommentBase):
    user_id: UUID
    task_id: UUID


class CommentUpdate(BaseModel):
    body: str | None = None


class CommentOut(CommentBase):
    id: UUID
    user_id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
