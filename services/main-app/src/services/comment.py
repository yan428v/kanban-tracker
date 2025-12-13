from uuid import UUID

from fastapi import Depends

from src.exceptions import CommentNotFoundError
from src.repositories import CommentRepository, get_comment_repository
from src.schemas import CommentCreate, CommentOut, CommentUpdate


class CommentService:
    def __init__(self, repository: CommentRepository):
        self.repository = repository

    async def get_all(
        self, task_id: UUID | None = None, user_id: UUID | None = None
    ) -> list[CommentOut]:
        comments = await self.repository.list(task_id=task_id, user_id=user_id)
        return comments

    async def get_by_id(self, comment_id: UUID) -> CommentOut:
        comment = await self.repository.get(comment_id)
        if comment is None:
            raise CommentNotFoundError(comment_id)
        return comment

    async def create(self, comment_data: CommentCreate) -> CommentOut:
        comment = await self.repository.create(
            body=comment_data.body,
            user_id=comment_data.user_id,
            task_id=comment_data.task_id,
        )
        return comment

    async def update(self, comment_id: UUID, comment_data: CommentUpdate) -> CommentOut:
        update_dict = {
            k: v
            for k, v in comment_data.model_dump(exclude_unset=True).items()
            if v is not None
        }

        if not update_dict:
            return await self.get_by_id(comment_id)

        comment = await self.repository.update(comment_id, **update_dict)
        if comment is None:
            raise CommentNotFoundError(comment_id)
        return comment

    async def delete(self, comment_id: UUID) -> None:
        deleted = await self.repository.delete(comment_id)
        if not deleted:
            raise CommentNotFoundError(comment_id)


async def get_comment_service(
    repository: CommentRepository = Depends(get_comment_repository),
) -> CommentService:
    return CommentService(repository)
