from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError

from auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
)
from auth.security import hash_password, verify_password
from core.config import auth_config
from models import RefreshToken, User
from repositories.refresh_token import (
    RefreshTokenRepository,
    get_refresh_token_repository,
)
from repositories.user import UserRepository, get_user_repository
from schemas.auth_schemas import (
    LogoutRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserRegister,
)


class AuthService:
    def __init__(
        self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def register(self, data: UserRegister) -> TokenPair:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_password = hash_password(data.password)

        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hashed_password,
        )
        user = await self.user_repo.create(user)

        return await self._create_token_pair(user.id)

    async def login(self, data: UserLogin) -> TokenPair:
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        return await self._create_token_pair(user.id)

    async def refresh(self, data: RefreshRequest) -> TokenPair:
        try:
            payload = decode_token(data.refresh_token, expected_type="refresh")
            jti = payload.get("jti")
            user_id = UUID(payload.get("sub"))

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from None

        token_in_db = await self.refresh_token_repo.get_by_jti(jti)

        if not token_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )

        if token_in_db.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        if token_in_db.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        access_token = create_access_token(user_id)

        return TokenPair(
            access_token=access_token,
            refresh_token=data.refresh_token,  # старый refresh
            token_type="bearer",
        )

    async def logout(self, data: LogoutRequest) -> None:
        try:
            payload = decode_token(data.refresh_token, expected_type="refresh")
            jti = payload.get("jti")

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            ) from None

        await self.refresh_token_repo.revoke(jti)

    async def _create_token_pair(self, user_id: UUID) -> TokenPair:
        access_token = create_access_token(user_id)
        jti = generate_jti()
        refresh_token = create_refresh_token(user_id, jti)

        expires_at = datetime.utcnow() + timedelta(
            days=auth_config.refresh_token_expire_days
        )
        token_in_db = RefreshToken(
            user_id=user_id,
            token_jti=jti,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self.refresh_token_repo.create(token_in_db)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(user_repo, refresh_token_repo)
