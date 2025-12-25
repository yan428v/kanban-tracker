from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        result = await self.db.execute(select(Notification).where(Notification.id == notification_id))

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Notification]:
        result = await self.db.execute(select(Notification).offset(skip).limit(limit))

        return result.scalars().all()

    async def create(self, notification_date: dict) -> Notification:
        notification = Notification(**notification_date)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def update(self, notification_id: UUID, notification_date: dict) -> Notification:
        notification = await self.get_by_id(notification_id)

        if notification:
            for key, value in notification_date.items():
                setattr(notification, key, value)

            await self.db.commit()
            await self.db.refresh(notification)

        return notification

    async def delete(self, notification_id: UUID) -> bool:
        notification = await self.get_by_id(notification_id)

        if notification:
            await self.db.delete(notification)
            await self.db.commit()

            return True

        return False


async def get_notification_reposetory(
    db: AsyncSession = Depends(get_session),
) -> NotificationRepository:
    return NotificationRepository(db)
