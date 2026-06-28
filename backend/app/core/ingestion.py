import logging
from datetime import datetime
from typing import Literal, Optional

from app.core.chunking import chunk_text
from app.core.embedding import embed_chunks
from app.core.parsing.pdf import extract_pdf_from_url
from app.core.parsing.web import scrape_url
from app.integrations.embeddings_api import EmbeddingsClient
from app.models.source import Source
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.source_repository import SourceRepository

logger = logging.getLogger(__name__)

# Chunk sizes tuned per source type
_CHUNK_SIZES: dict[str, tuple[int, int]] = {
    "resume": (400, 50),
    "url": (500, 75),
}


async def ingest_source(
    source_repo: SourceRepository,
    chunk_repo: ChunkRepository,
    embeddings_client: EmbeddingsClient,
    *,
    source_type: Literal["resume", "url"],
    label: str,
    url: Optional[str] = None,
    file_path: Optional[str] = None,
    existing_source: Optional[Source] = None,
) -> Source:
    """Full inline pipeline: parse → chunk → embed → store.

    Does NOT commit — the calling router controls the transaction boundary.
    Raises on any failure; the caller's transaction rolls back automatically.
    """
    source_id = str(existing_source.id) if existing_source else "new"
    logger.info("ingest.started source_id=%s type=%s label=%s", source_id, source_type, label)

    # 1. Parse
    if source_type == "resume":
        assert file_path is not None
        text = await extract_pdf_from_url(file_path)  # file_path holds the Cloudinary URL
    else:
        assert url is not None
        text = await scrape_url(url)

    logger.info("ingest.extracted source_id=%s chars=%d", source_id, len(text))

    # 2. Chunk
    chunk_size, overlap = _CHUNK_SIZES[source_type]
    texts = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    logger.info("ingest.chunked source_id=%s chunks=%d", source_id, len(texts))

    # 3. Embed
    embeddings = await embed_chunks(embeddings_client, texts)
    logger.info("ingest.embedded source_id=%s", source_id)

    # 4. Store
    now = datetime.utcnow()  # naive UTC — matches TIMESTAMP WITHOUT TIME ZONE column

    if existing_source:
        await chunk_repo.delete_by_source(existing_source.id)
        source = await source_repo.update(
            existing_source,
            status="ready",
            error=None,
            chunk_count=len(texts),
            indexed_at=now,
        )
    else:
        if source_type == "resume":
            old = await source_repo.get_resume()
            if old:
                # Only one resume is meaningful at a time; old one deleted before new one lands
                await source_repo.delete(old)  # chunks cascade via FK

        source = await source_repo.create(
            type=source_type,
            label=label,
            url=url,
            file_path=file_path,
            status="ready",
            chunk_count=len(texts),
            indexed_at=now,
        )

    await chunk_repo.insert_chunks(
        source.id,
        texts,
        embeddings,
        metadata={"label": label, "source_type": source_type},
    )

    logger.info("ingest.committed source_id=%s chunks=%d", source.id, len(texts))
    return source
