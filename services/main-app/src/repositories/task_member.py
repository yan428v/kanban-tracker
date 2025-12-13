from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from exceptions import TaskMemberAlreadyExistsError
from models import TaskMember


class TaskMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task_member: TaskMember) -> TaskMember:
        self.db.add(task_member)
        try:
            await self.db.commit()
            await self.db.refresh(task_member)
            return task_member
        except IntegrityError as e:
            await self.db.rollback()
            if "uq_task_member_user_task" in str(e.orig):
                raise TaskMemberAlreadyExistsError(
                    task_member.task_id, task_member.user_id
                ) from e
            raise

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        task_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[TaskMember]:
        query = select(TaskMember)
        if task_id is not None:
            query = query.where(TaskMember.task_id == task_id)
        if user_id is not None:
            query = query.where(TaskMember.user_id == user_id)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def delete(self, task_id: UUID, user_id: UUID) -> None:
        stmt = delete(TaskMember).where(
            TaskMember.task_id == task_id, TaskMember.user_id == user_id
        )
        await self.db.execute(stmt)
        await self.db.commit()


async def get_task_member_repository(
    db: AsyncSession = Depends(get_session),
) -> TaskMemberRepository:
    return TaskMemberRepository(db)
