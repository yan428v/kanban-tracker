from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.dependencies import get_current_user
from models import User
from schemas.auth_schemas import (
    LogoutRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserRegister,
)
from schemas.user_schema import UserResponse
from services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя и возвращает пару токенов (access + refresh)",
)
async def register(
    data: UserRegister,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(data)


@router.post(
    "/token",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="Получить токен (OAuth2)",
    description="Эндпоинт для OAuth2PasswordBearer. Используется Swagger UI для авторизации.",
)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await service.login(login_data)


@router.post(
    "/login",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему (JSON)",
    description="Аутентифицирует пользователя и возвращает пару токенов",
)
async def login(
    data: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов",
    description="Создает новый access token используя refresh token (reuse стратегия)",
)
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
    description="Отзывает refresh token (делает его невалидным)",
)
async def logout(
    data: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем аутентифицированном пользователе",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
