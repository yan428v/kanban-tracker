from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeamMemberCreateRequest(BaseModel):
    team_id: UUID
    user_id: UUID


class TeamMemberUpdateRequest(BaseModel):
    team_id: Optional[UUID] = None
    user_id: Optional[UUID] = None


class TeamMemberResponse(BaseModel):
    id: UUID
    team_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

