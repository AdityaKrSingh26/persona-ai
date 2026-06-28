import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies.auth import require_admin
from app.dependencies.providers import get_source_repo
from app.repositories.source_repository import SourceRepository
from app.schemas import SourceResponse

router = APIRouter(prefix="/sources", tags=["sources"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[SourceResponse])
async def list_sources(
    _payload: dict = Depends(require_admin),
    source_repo: SourceRepository = Depends(get_source_repo),
):
    sources = await source_repo.list_all()
    logger.info("[sources] list all | count=%d", len(sources))
    return [SourceResponse.model_validate(s) for s in sources]


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: uuid.UUID,
    _payload: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    source_repo: SourceRepository = Depends(get_source_repo),
):
    source = await source_repo.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    logger.info("[sources] delete | source_id=%s", source_id)
    await source_repo.delete(source)
    await db.commit()
    return Response(status_code=204)
