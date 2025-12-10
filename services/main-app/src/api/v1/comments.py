from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.schemas import CommentCreate, CommentOut, CommentUpdate
from src.services.comment import CommentService, get_comment_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=list[CommentOut])
async def list_comments(
    task_id: UUID | None = Query(None, description="Фильтр по задаче"),
    user_id: UUID | None = Query(None, description="Фильтр по пользователю"),
    service: CommentService = Depends(get_comment_service),
) -> list[CommentOut]:
    return await service.get_all(task_id=task_id, user_id=user_id)


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
) -> CommentOut:
    return await service.get_by_id(comment_id)


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreate,
    service: CommentService = Depends(get_comment_service),
) -> CommentOut:
    return await service.create(payload)


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: UUID,
    payload: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
) -> CommentOut:
    return await service.update(comment_id, payload)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
) -> None:
    await service.delete(comment_id)
