import re

from pydantic import BaseModel, EmailStr, field_validator


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля: мин 8 символов, uppercase, lowercase, digit, special char"""
        errors = []

        if len(v) < 8:
            errors.append("не менее 8 символов")

        if not re.search(r"[A-Z]", v):
            errors.append("хотя бы одну заглавную латинскую букву")

        if not re.search(r"[a-z]", v):
            errors.append("хотя бы одну строчную латинскую букву")

        if not re.search(r"\d", v):
            errors.append("хотя бы одну цифру")

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', v):
            errors.append("хотя бы один специальный символ")

        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
