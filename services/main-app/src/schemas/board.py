from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateBoardRequest(BaseModel):
    title: str
    description: str | None = None
    is_public: bool = False
    owner_id: UUID
    team_id: UUID | None = None


class UpdateBoardRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None
    team_id: UUID | None = None


class BoardResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_public: bool
    owner_id: UUID
    team_id: UUID | None
    created_at: datetime
    updated_at: datetime
