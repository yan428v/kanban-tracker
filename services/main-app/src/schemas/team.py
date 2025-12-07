from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class TeamUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

