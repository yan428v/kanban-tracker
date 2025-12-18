from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from models import BoardColumn, User
from schemas.column import ColumnResponse, CreateColumnRequest, UpdateColumnRequest
from services.column import ColumnService, get_column_service

router = APIRouter()

COLUMN_NOT_FOUND_MESSAGE = "Column not found"


@router.get("/columns", response_model=list[ColumnResponse])
async def list_columns(
    skip: int | None = Query(None),
    limit: int | None = Query(None),
    service: ColumnService = Depends(get_column_service),
    current_user: User = Depends(get_current_user),
):
    if skip is None:
        skip = 0
    elif skip < 0:
        skip = 0

    if limit is None:
        limit = 100
    else:
        limit = min(limit, 1000)

    columns = await service.get_many(skip=skip, limit=limit)
    return [column_to_response(column) for column in columns]


@router.get("/columns/{column_id}", response_model=ColumnResponse)
async def get_column(
    column_id: UUID,
    service: ColumnService = Depends(get_column_service),
    current_user: User = Depends(get_current_user),
):
    column = await service.get(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COLUMN_NOT_FOUND_MESSAGE
        )
    return column_to_response(column)


@router.post(
    "/columns", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED
)
async def create_column(
    column_data: CreateColumnRequest,
    service: ColumnService = Depends(get_column_service),
    current_user: User = Depends(get_current_user),
):
    column = await service.create(column_data)
    return column_to_response(column)


@router.patch("/columns/{column_id}", response_model=ColumnResponse)
async def update_column(
    column_id: UUID,
    column_data: UpdateColumnRequest,
    service: ColumnService = Depends(get_column_service),
    current_user: User = Depends(get_current_user),
):
    column = await service.update(column_id, column_data)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COLUMN_NOT_FOUND_MESSAGE
        )
    return column_to_response(column)


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: UUID,
    service: ColumnService = Depends(get_column_service),
    current_user: User = Depends(get_current_user),
):
    result = await service.delete(column_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COLUMN_NOT_FOUND_MESSAGE
        )


def column_to_response(column: BoardColumn) -> ColumnResponse:
    return ColumnResponse(
        id=column.id,
        title=column.title,
        position=column.position,
        limit=column.limit,
        board_id=column.board_id,
        created_at=column.created_at,
        updated_at=column.updated_at,
    )
