from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings

ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 1


def verify_password(plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), settings.admin_password_hash.encode())


def sign_token(token_version: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "admin",
        # ver in the token is checked against DB on every request — lets logout invalidate all sessions
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # Raises jose.JWTError on expiry, bad signature, or malformed token
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
