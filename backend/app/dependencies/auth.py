import logging

from fastapi import Cookie, Depends, HTTPException, Request
from jose import JWTError

from app.core.security import decode_token
from app.dependencies.providers import get_meta_repo
from app.repositories.meta_repository import MetaRepository

logger = logging.getLogger(__name__)


async def require_admin(
    # HttpOnly cookie keeps the token out of JS — XSS-safe without an Authorization header
    admin_token: str | None = Cookie(default=None),
    meta: MetaRepository = Depends(get_meta_repo),
) -> dict:
    if admin_token is None:
        logger.warning("[auth] rejected — no cookie")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(admin_token)
    except JWTError as exc:
        logger.warning("[auth] rejected — bad JWT: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    server_version = await meta.get_token_version()
    token_ver = payload.get("ver")
    if token_ver != server_version:
        logger.warning("[auth] rejected — version mismatch token=%s server=%s", token_ver, server_version)
        raise HTTPException(status_code=401, detail="Session revoked")

    logger.debug("[auth] ok | sub=%s", payload.get("sub"))
    return payload
