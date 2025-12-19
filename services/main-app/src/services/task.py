from uuid import UUID

from fastapi import Depends

from models import Task
from repositories.task import TaskRepository, get_task_reposetory
from repositories.notification import NotificationRepository, get_notification_reposetory
from schemas.task import CreateTaskRequest, UpdateTaskRequest


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        notification_repository: NotificationRepository
    ):
        self.task_repository = task_repository
        self.notification_repository = notification_repository

    async def get(self, task_id: UUID) -> Task | None:
        return await self.task_repository.get_by_id(task_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[Task]:
        return await self.task_repository.get_all(skip=skip, limit=limit)

    async def create(self, task_data: CreateTaskRequest) -> Task:
        data = {
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status,
            "due_date": task_data.due_date,
            "user_id": task_data.user_id,
            "column_id": task_data.column_id,
        }
        task = await self.task_repository.create(data)
        await self.notification_repository.create({
            "message": f"Task `{task.title}` has been created",
            "user_id": task.user_id,
            "task_id": task.id
        })
        return task

    async def update(self, task_id: UUID, task_data: UpdateTaskRequest) -> Task:
        data, notification_data = {}
        if task_data.title is not None:
            data["title"] = task_data.title
        if task_data.description is not None:
            data["description"] = task_data.description
        if task_data.status is not None:
            data["status"] = task_data.status
        if task_data.due_date is not None:
            data["due_date"] = task_data.due_date
        if task_data.column_id is not None:
            data["column_id"] = task_data.column_id

        task = await self.task_repository.update(task_id, data)
        await self.notification_repository.create({
            "message": f"Task `{task.title}` has been updated",
            "user_id": task.user_id,
            "task_id": task_id
        })
        await self.notification_repository.update()
        return task

    async def delete(self, task_id: UUID) -> bool:
        task = self.task_repository.get_by_id(task_id)
        await self.notification_repository.create({
            "message": f"Task `{task.title}` has been deleted",
            "user_id": task.user_id,
            "task_id": task_id
        })
        await self.task_repository.delete(task_id)


async def get_task_service(
    task_repository: TaskRepository = Depends(get_task_reposetory),
    notification_repository: NotificationRepository = Depends(get_notification_reposetory)
) -> TaskService:
    return TaskService(task_repository, notification_repository)