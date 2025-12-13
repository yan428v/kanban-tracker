from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from exceptions import TaskMemberAlreadyExistsError
from models import TaskMember
from schemas.task_member import CreateTaskMemberRequest, TaskMemberResponse
from services.task_member import TaskMemberService, get_task_member_service

router = APIRouter(prefix="/task-members", tags=["task-members"])


@router.get("/", response_model=list[TaskMemberResponse])
async def list_task_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0, le=1000),
    task_id: UUID | None = None,
    user_id: UUID | None = None,
    service: TaskMemberService = Depends(get_task_member_service),
):
    members = await service.get_many(
        skip=skip,
        limit=limit,
        task_id=task_id,
        user_id=user_id,
    )
    return [task_member_to_response(member) for member in members]


@router.post(
    "/",
    response_model=TaskMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_member(
    payload: CreateTaskMemberRequest,
    service: TaskMemberService = Depends(get_task_member_service),
):
    try:
        member = await service.create(payload)
        return task_member_to_response(member)
    except TaskMemberAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_member(
    task_id: UUID,
    user_id: UUID,
    service: TaskMemberService = Depends(get_task_member_service),
):
    await service.delete(task_id=task_id, user_id=user_id)


def task_member_to_response(member: TaskMember) -> TaskMemberResponse:
    return TaskMemberResponse(
        id=member.id,
        task_id=member.task_id,
        user_id=member.user_id,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )
