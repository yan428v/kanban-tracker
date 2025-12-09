from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from models import Task


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: UUID) -> Task | None:
        result = await self.db.execute(select(Task).where(Task.id == task_id))

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Task]:
        result = await self.db.execute(select(Task).offset(skip).limit(limit))

        return result.scalars().all()

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
        )

        return result.scalars().all()

    async def get_by_column_id(
        self, column_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(Task.column_id == column_id).offset(skip).limit(limit)
        )

        return result.scalars().all()

    async def create(self, task_date: dict) -> Task:
        task = Task(**task_date)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: UUID, task_date: dict) -> Task:
        task = await self.get_by_id(task_id)

        if task:
            for key, value in task_date.items():
                setattr(task, key, value)

            await self.db.commit()
            await self.db.refresh(task)

        return task

    async def delete(self, task_id: UUID) -> bool:
        task = await self.get_by_id(task_id)

        if task:
            await self.db.delete(task)
            await self.db.commit()

            return True

        return False

    async def search_by_title(
        self, title_pattern: str, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await self.db.execute(
            select(Task)
            .where(Task.title.ilike(f"%{title_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


async def get_task_reposetory(
    db: AsyncSession = Depends(get_session),
) -> TaskRepository:
    return TaskRepository(db)
