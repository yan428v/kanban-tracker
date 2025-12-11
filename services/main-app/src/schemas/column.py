from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateColumnRequest(BaseModel):
    title: str
    position: int = 0
    limit: int | None = None
    board_id: UUID


class UpdateColumnRequest(BaseModel):
    title: str | None = None
    position: int | None = None
    limit: int | None = None


class ColumnResponse(BaseModel):
    id: UUID
    title: str
    position: int
    limit: int | None
    board_id: UUID
    created_at: datetime
    updated_at: datetime
