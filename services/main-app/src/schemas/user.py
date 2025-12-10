# app/schemas/user.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# Базовая схема с общими полями
class UserBase(BaseModel):
    name: str
    email: EmailStr


# Для создания - только то, что клиент может передать
class UserCreate(UserBase):
    pass


# Для обновления - все поля опциональны
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


# Для ответа - включает служебные поля
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )  # для конвертации из SQLAlchemy модели
