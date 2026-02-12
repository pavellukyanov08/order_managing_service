from datetime import datetime
from typing import Any

import jwt
from app.settings import jwt_settings
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()


class JWTAuth:
    def __init__(
        self,
        *,
        secret_key: str = jwt_settings.jwt_secret_key,
        algorithm: str = "HS256",
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def encode_token(
        self,
        *,
        payload: dict[str, Any],
        expire_minutes: datetime,
    ) -> str:
        to_encode = payload.copy()
        to_encode.update(
            exp=expire_minutes,
        )
        return jwt.encode(
            to_encode,
            self._secret_key,
            algorithm=self._algorithm,
        )

    def decode_token(self, *, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )


class PasswordManager:
    _pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_hashed_password(cls, password: str) -> str:
        return cls._pwd_context.hash(secret=password)

    @classmethod
    def verify_password(cls, user_password: str, hashed_password: str) -> bool:
        return cls._pwd_context.verify(user_password, hashed_password)


jwt_auth = JWTAuth()
password_manager = PasswordManager()