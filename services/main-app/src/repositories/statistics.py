from datetime import UTC, datetime, timedelta

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from enums.task_status import TaskStatus
from models import Board, Comment, Task, TaskMember, Team, User


class StatisticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entity_counts(self) -> dict[str, int]:
        teams_result = await self.db.execute(select(func.count(Team.id)))
        users_result = await self.db.execute(select(func.count(User.id)))
        boards_result = await self.db.execute(select(func.count(Board.id)))
        tasks_result = await self.db.execute(select(func.count(Task.id)))
        comments_result = await self.db.execute(select(func.count(Comment.id)))

        return {
            "teams": teams_result.scalar() or 0,
            "users": users_result.scalar() or 0,
            "boards": boards_result.scalar() or 0,
            "tasks": tasks_result.scalar() or 0,
            "comments": comments_result.scalar() or 0,
        }

    async def get_tasks_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Task.status, func.count(Task.id)).group_by(Task.status)
        )
        rows = result.all()
        status_counts = {status.value: count for status, count in rows}
        for status in TaskStatus:
            if status.value not in status_counts:
                status_counts[status.value] = 0
        return status_counts

    async def get_tasks_by_assignee(self) -> list[dict]:
        result = await self.db.execute(
            select(TaskMember.user_id, func.count(TaskMember.task_id))
            .group_by(TaskMember.user_id)
        )
        rows = result.all()
        return [{"user_id": user_id, "count": count} for user_id, count in rows]

    async def get_due_date_health(self) -> dict[str, int]:
        now_utc = datetime.now(UTC)
        now = now_utc.replace(tzinfo=None)
        due_soon_threshold = now + timedelta(days=7)

        overdue_result = await self.db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.due_date < now,
                    Task.status != TaskStatus.COMPLETED,
                )
            )
        )

        due_soon_result = await self.db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.due_date >= now,
                    Task.due_date < due_soon_threshold,
                    Task.status != TaskStatus.COMPLETED,
                )
            )
        )

        missing_due_date_result = await self.db.execute(
            select(func.count(Task.id)).where(Task.due_date.is_(None))
        )

        return {
            "overdue_count": overdue_result.scalar() or 0,
            "due_soon_count": due_soon_result.scalar() or 0,
            "missing_due_date_count": missing_due_date_result.scalar() or 0,
        }

async def get_statistics_repository(
    db: AsyncSession = Depends(get_session),
) -> StatisticsRepository:
    return StatisticsRepository(db)

