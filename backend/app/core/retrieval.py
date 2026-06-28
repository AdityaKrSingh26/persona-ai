from app.core.embedding import embed_query
from app.integrations.embeddings_api import EmbeddingsClient
from app.repositories.chunk_repository import ChunkRepository

# Threshold of 0.3 is the deliberate correction from v1.0 (0.75 was too high —
# cosine similarity for relevant-but-differently-worded text often sits at 0.3–0.5)
DEFAULT_MIN_SIMILARITY = 0.15


async def retrieve(
    chunk_repo: ChunkRepository,
    embeddings_client: EmbeddingsClient,
    query: str,
    top_k: int = 5,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
) -> list:
    query_embedding = await embed_query(embeddings_client, query)
    return await chunk_repo.search_similar(query_embedding, top_k, min_similarity)


