import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.ingestion import ingest_source
from app.db import get_db
from app.dependencies.auth import require_admin
from app.dependencies.providers import (
    get_chunk_repo,
    get_embeddings_client,
    get_source_repo,
)
from app.integrations.cloudinary import upload_pdf
from app.integrations.embeddings_api import EmbeddingsClient
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.source_repository import SourceRepository
from app.schemas import IngestUrlRequest, SourceResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = logging.getLogger(__name__)

_MB = 1024 * 1024


@router.post("/resume", response_model=SourceResponse)
async def ingest_resume(
    file: UploadFile = File(...),
    _payload: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    source_repo: SourceRepository = Depends(get_source_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embeddings_client: EmbeddingsClient = Depends(get_embeddings_client),
):
    if file.content_type != "application/pdf" or not (file.filename or "").endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are accepted")

    content = await file.read()
    logger.info("[ingest] upload resume | file=%s size=%dKB", file.filename, len(content) // 1024)
    if len(content) > settings.max_upload_size_mb * _MB:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit")

    # Upload to Cloudinary before opening a transaction — Render has an ephemeral filesystem
    cloudinary_url = await upload_pdf(content, filename=f"resume_{uuid.uuid4()}")

    try:
        source = await ingest_source(
            source_repo, chunk_repo, embeddings_client,
            source_type="resume", label="Resume", file_path=cloudinary_url,
        )
        await db.commit()
        return SourceResponse.model_validate(source)
    except Exception as exc:
        await db.rollback()
        logger.error("[ingest] resume failed | error=%s", exc)
        # Commit a failed source row so the dashboard can show re-index
        try:
            failed = await source_repo.create(
                type="resume", label="Resume",
                file_path=cloudinary_url, status="failed", error=str(exc),
            )
            await db.commit()
            return SourceResponse.model_validate(failed)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(exc))


@router.post("/url", response_model=SourceResponse)
async def ingest_url(
    body: IngestUrlRequest,
    _payload: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    source_repo: SourceRepository = Depends(get_source_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embeddings_client: EmbeddingsClient = Depends(get_embeddings_client),
):
    url_str = str(body.url)
    logger.info("[ingest] ingest url | url=%s label=%s", url_str, body.label)

    # Pre-flight reachability check before opening a transaction
    is_linkedin = "linkedin.com" in url_str.lower()
    if not is_linkedin:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                try:
                    resp = await client.head(url_str, follow_redirects=True)
                    resp.raise_for_status()
                except (httpx.HTTPStatusError, httpx.RequestError):
                    # Fallback to GET in case HEAD is not allowed/supported
                    resp = await client.get(url_str, follow_redirects=True)
                    resp.raise_for_status()
        except Exception as exc:
            logger.warning("[ingest] pre-flight reachability check failed for url=%s: %s", url_str, exc)
            raise HTTPException(status_code=422, detail="URL is not reachable")

    try:
        source = await ingest_source(
            source_repo, chunk_repo, embeddings_client,
            source_type="url", label=body.label, url=url_str,
        )
        await db.commit()
        return SourceResponse.model_validate(source)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A source with this URL already exists")
    except Exception as exc:
        await db.rollback()
        logger.error("[ingest] url failed | url=%s error=%s", url_str, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{source_id}/reindex", response_model=SourceResponse)
async def reindex_source(
    source_id: uuid.UUID,
    _payload: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    source_repo: SourceRepository = Depends(get_source_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embeddings_client: EmbeddingsClient = Depends(get_embeddings_client),
):
    source = await source_repo.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    logger.info("[ingest] reindex | source_id=%s type=%s", source_id, source.type)

    try:
        updated = await ingest_source(
            source_repo, chunk_repo, embeddings_client,
            source_type=source.type,  # type: ignore[arg-type]
            label=source.label, url=source.url, file_path=source.file_path,
            existing_source=source,
        )
        await db.commit()
        return SourceResponse.model_validate(updated)
    except Exception as exc:
        await db.rollback()
        logger.error("[ingest] reindex failed | source_id=%s error=%s", source_id, exc)
        # Commit a failed status so the dashboard shows the error and offers re-index
        try:
            failed = await source_repo.update(source, status="failed", error=str(exc))
            await db.commit()
            return SourceResponse.model_validate(failed)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(exc))
