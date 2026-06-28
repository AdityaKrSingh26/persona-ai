import asyncio
import logging

import httpx

from app.integrations.embeddings_api import EmbeddingsClient

logger = logging.getLogger(__name__)

_MAX_RETRIES = 4


async def embed_chunks(
    client: EmbeddingsClient,
    texts: list[str],
    batch_size: int = 16,
) -> list[list[float]]:
    """Embed a list of texts in batches with exponential backoff on rate limits."""
    results: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        for attempt in range(_MAX_RETRIES):
            try:
                embeddings = await client.embed(batch)
                results.extend(embeddings)
                break
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429 and attempt < _MAX_RETRIES - 1:
                    wait = 2**attempt
                    logger.warning("embed rate-limited, retrying in %ds (attempt %d)", wait, attempt + 1)
                    await asyncio.sleep(wait)
                else:
                    raise

    return results


async def embed_query(client: EmbeddingsClient, query: str) -> list[float]:
    # Reuses batch path so retry logic applies uniformly to single-query calls too
    return (await embed_chunks(client, [query]))[0]
