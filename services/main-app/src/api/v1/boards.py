from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from models import Board, User
from schemas.board import BoardResponse, CreateBoardRequest, UpdateBoardRequest
from services.board import BoardService, get_board_service

router = APIRouter()

BOARD_NOT_FOUND_MESSAGE = "Board not found"


@router.get("/boards", response_model=list[BoardResponse])
async def list_boards(
    skip: int | None = Query(None),
    limit: int | None = Query(None),
    service: BoardService = Depends(get_board_service),
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

    boards = await service.get_many(skip=skip, limit=limit)
    return [board_to_response(board) for board in boards]


@router.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: UUID,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    board = await service.get(board_id)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )
    return board_to_response(board)


@router.post("/boards", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: CreateBoardRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    board = await service.create(board_data)
    return board_to_response(board)


@router.patch("/boards/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: UUID,
    board_data: UpdateBoardRequest,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    board = await service.update(board_id, board_data)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )
    return board_to_response(board)


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    service: BoardService = Depends(get_board_service),
    current_user: User = Depends(get_current_user),
):
    result = await service.delete(board_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )


def board_to_response(board: Board) -> BoardResponse:
    return BoardResponse(
        id=board.id,
        title=board.title,
        description=board.description,
        is_public=board.is_public,
        owner_id=board.owner_id,
        team_id=board.team_id,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )
