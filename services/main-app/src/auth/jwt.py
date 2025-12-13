import uuid
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from jose import JWTError, jwt

from core.config import auth_config

SECRET_KEY = auth_config.secret_key
ALGORITHM = auth_config.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = auth_config.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = auth_config.refresh_token_expire_days


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID, jti: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        token_type = payload.get("type")
        if token_type != expected_type:
            raise JWTError(
                f"Invalid token type. Expected '{expected_type}', got '{token_type}'"
            )

        return payload

    except JWTError as e:
        raise e


def generate_jti() -> str:
    return str(uuid.uuid4())
