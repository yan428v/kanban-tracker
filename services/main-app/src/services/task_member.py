from uuid import UUID

from fastapi import Depends

from models import TaskMember
from repositories.task_member import (
    TaskMemberRepository,
    get_task_member_repository,
)
from schemas.task_member import CreateTaskMemberRequest


class TaskMemberService:
    def __init__(self, repository: TaskMemberRepository):
        self.repository = repository

    async def create(self, data: CreateTaskMemberRequest) -> TaskMember:
        task_member = TaskMember(
            task_id=data.task_id,
            user_id=data.user_id,
        )
        return await self.repository.create(task_member)

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        task_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[TaskMember]:
        return await self.repository.get_many(
            skip=skip,
            limit=limit,
            task_id=task_id,
            user_id=user_id,
        )

    async def delete(self, task_id: UUID, user_id: UUID) -> None:
        await self.repository.delete(task_id, user_id)


async def get_task_member_service(
    repository: TaskMemberRepository = Depends(get_task_member_repository),
) -> TaskMemberService:
    return TaskMemberService(repository)
