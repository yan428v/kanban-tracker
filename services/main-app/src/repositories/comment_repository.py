from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, task_id: UUID | None = None, user_id: UUID | None = None
    ) -> list[Comment]:
        query = select(Comment)
        if task_id:
            query = query.where(Comment.task_id == task_id)
        if user_id:
            query = query.where(Comment.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get(self, comment_id: UUID) -> Comment | None:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, body: str, user_id: UUID, task_id: UUID) -> Comment:
        comment = Comment(body=body, user_id=user_id, task_id=task_id)
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def update(
        self, comment_id: UUID, *, body: str | None = None
    ) -> Comment | None:
        update_data = {}
        if body is not None:
            update_data["body"] = body
        if not update_data:
            return await self.get(comment_id)

        stmt = (
            update(Comment)
            .where(Comment.id == comment_id)
            .values(**update_data)
            .returning(Comment)
        )
        result = await self.session.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment is None:
            return None
        await self.session.commit()
        return comment

    async def delete(self, comment_id: UUID) -> bool:
        result = await self.session.execute(
            delete(Comment).where(Comment.id == comment_id).returning(Comment.id)
        )
        deleted_id = result.scalar_one_or_none()
        if deleted_id is None:
            return False
        await self.session.commit()
        return True


async def get_comment_repository(
    session: AsyncSession = Depends(get_session),
) -> CommentRepository:
    return CommentRepository(session)
