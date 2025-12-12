from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from models import Task
from schemas.task import CreateTaskRequest, TaskResponse, UpdateTaskRequest
from services.task import TaskService, get_task_service

router = APIRouter()

TASK_NOT_FOUND_MESSAGE = "Task not found"


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service),
):
    tasks = await service.get_many(skip=skip, limit=limit)
    return [task_to_response(task) for task in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    task = await service.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )
    return task_to_response(task)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: CreateTaskRequest,
    service: TaskService = Depends(get_task_service),
):
    task = await service.create(task_data)
    return task_to_response(task)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: UpdateTaskRequest,
    service: TaskService = Depends(get_task_service),
):
    task = await service.update(task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )
    return task_to_response(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    result = await service.delete(task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )


def task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        user_id=task.user_id,
        column_id=task.column_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
