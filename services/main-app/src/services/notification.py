from uuid import UUID

from fastapi import Depends

from models import Notification
from repositories.notification import NotificationRepository, get_notification_reposetory
from schemas.notification import CreateNotificationRequest, UpdateNotificationRequest


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def get(self, notification_id: UUID) -> Notification | None:
        return await self.repository.get_by_id(notification_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[Notification]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, notification_data: CreateNotificationRequest) -> Notification:
        data = {
            "message": notification_data.message,
            "user_id": notification_data.user_id,
            "task_id": notification_data.task_id,
        }
        return await self.repository.create(data)

    async def update(self, notification_id: UUID, notification_data: UpdateNotificationRequest) -> Notification:
        data = {}
        if notification_data.message is not None:
            data["message"] = notification_data.message
        if notification_data.user_id is not None:
            data["user_id"] = notification_data.user_id
        if notification_data.task_id is not None:
            data["task_id"] = notification_data.task_id

        return await self.repository.update(notification_id, data)

    async def delete(self, notification_id: UUID) -> bool:
        return await self.repository.delete(notification_id)


async def get_notification_service(
    repository: NotificationRepository = Depends(get_notification_reposetory),
) -> NotificationService:
    return NotificationService(repository)
