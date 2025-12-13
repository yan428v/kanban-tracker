from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from auth.jwt import decode_token
from exceptions import InvalidCredentialsError
from models import User
from repositories.user import UserRepository, get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        payload = decode_token(token, expected_type="access")
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise InvalidCredentialsError()

        user_id = UUID(user_id_str)

    except JWTError:
        raise InvalidCredentialsError() from None
    except ValueError:
        raise InvalidCredentialsError() from None

    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise InvalidCredentialsError()

    return user
