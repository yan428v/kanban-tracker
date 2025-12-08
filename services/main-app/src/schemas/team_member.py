from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateTeamMemberRequest(BaseModel):
    team_id: UUID
    user_id: UUID


class TeamMemberResponse(BaseModel):
    id: UUID
    team_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
