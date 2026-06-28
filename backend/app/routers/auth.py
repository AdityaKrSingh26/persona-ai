import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import sign_token, verify_password
from app.db import get_db
from app.dependencies.auth import require_admin
from app.dependencies.providers import get_meta_repo
from app.repositories.meta_repository import MetaRepository
from app.schemas import LoginRequest, MeResponse
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    meta: MetaRepository = Depends(get_meta_repo),
    db: AsyncSession = Depends(get_db),
):
    client = request.client.host if request.client else "unknown"
    if not verify_password(body.password):
        logger.warning("[auth] login failed — wrong password | client=%s", client)
        raise HTTPException(status_code=401, detail="Incorrect password")

    version = await meta.get_token_version()
    token = sign_token(version)
    samesite = "none" if settings.is_prod else "lax"
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite=samesite,
        secure=settings.is_prod,
        max_age=3600,
    )
    logger.info("[auth] admin logged in | client=%s | secure_cookie=%s", client, settings.is_prod)
    return {"ok": True}


@router.get("/me", response_model=MeResponse)
async def me(payload: dict = Depends(require_admin)):
    logger.debug("[auth] me check | sub=%s", payload.get("sub"))
    return MeResponse(sub=payload["sub"])


@router.post("/logout")
async def logout(
    response: Response,
    payload: dict = Depends(require_admin),
    meta: MetaRepository = Depends(get_meta_repo),
    db: AsyncSession = Depends(get_db),
):
    await meta.bump_token_version()
    await db.commit()
    samesite = "none" if settings.is_prod else "lax"
    response.delete_cookie(
        "admin_token",
        httponly=True,
        samesite=samesite,
        secure=settings.is_prod,
    )
    logger.info("[auth] admin logged out | sub=%s", payload.get("sub"))
    return {"ok": True}
