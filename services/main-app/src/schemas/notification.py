from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateNotificationRequest(BaseModel):
    message: str
    user_id: UUID
    task_id: UUID

    
class UpdateNotificationRequest(BaseModel):
    message: str | None = None
    user_id: UUID | None = None
    task_id: UUID | None = None


class NotificationResponse(BaseModel):
    id: UUID
    message: str
    user_id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime
