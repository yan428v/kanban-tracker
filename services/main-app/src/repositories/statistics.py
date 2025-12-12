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
        now = datetime.now(UTC)
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

    async def get_completed_history(self, weeks: int = 12) -> list[dict]:
        now = datetime.now(UTC).replace(tzinfo=None)
        current_week_start = now - timedelta(days=now.weekday())
        current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        weeks_back = weeks - 1
        start_date = current_week_start - timedelta(weeks=weeks_back)

        result = await self.db.execute(
            select(
                func.date_trunc("week", Task.completed_at).label("week_start"),
                func.count(Task.id).label("completed_count"),
            )
            .where(
                and_(
                    Task.completed_at.isnot(None),
                    Task.completed_at >= start_date,
                    Task.completed_at < current_week_start + timedelta(weeks=1),
                )
            )
            .group_by(func.date_trunc("week", Task.completed_at))
            .order_by(func.date_trunc("week", Task.completed_at))
        )

        rows = result.all()
        week_counts = {}
        for row in rows:
            week_start = row.week_start
            if week_start.tzinfo is not None:
                week_start = week_start.replace(tzinfo=None)
            week_counts[week_start] = row.completed_count

        history = []
        for i in range(weeks):
            week_start = start_date + timedelta(weeks=i)
            count = week_counts.get(week_start, 0)
            history.append({"week_start": week_start, "completed_count": count})

        return history


async def get_statistics_repository(
    db: AsyncSession = Depends(get_session),
) -> StatisticsRepository:
    return StatisticsRepository(db)

