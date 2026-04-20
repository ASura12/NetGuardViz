from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from app.core.config import JWT_SECRET, JWT_EXPIRE_MINUTES


class JWTService:

    SECRET = JWT_SECRET or "dev-secret-change-me"
    ALGORITHM = "HS256"
    EXPIRY_TIME_IN_MINUTES = JWT_EXPIRE_MINUTES


    def encode(self, email: str, role: str) -> str:

        payload = {
            "sub": email,
            "role" : role
        }

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JWTService.EXPIRY_TIME_IN_MINUTES
        )

        payload: dict[str, Any] = {
            "sub": email,
            "role": role
        }
        payload["exp"] = expire

        token = jwt.encode(
            payload,
            JWTService.SECRET,
            algorithm=JWTService.ALGORITHM
        )

        return token


    def decode(self, token: str) -> dict[str, Any] | None:

        try:
            payload = jwt.decode(
                token,
                JWTService.SECRET,
                algorithms=[JWTService.ALGORITHM]
            )

            return payload

        except JWTError as ex:
            print(f"JWT Decode Error: {str(ex)}")
            return None