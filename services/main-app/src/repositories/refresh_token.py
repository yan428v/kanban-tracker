from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke(self, jti: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_jti == jti)
            .values(is_revoked=True)
        )
        await self.db.commit()

    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.db.commit()

    async def delete_expired(self) -> None:
        """
        Удалить все истекшие токены из БД (очистка). Вызывать периодически
            для очистки старых записей.#todo celery or background task
        """
        from datetime import datetime

        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        )
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await self.db.delete(token)

        await self.db.commit()

    async def get_user_tokens(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_refresh_token_repository(
    db: AsyncSession = Depends(get_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)
