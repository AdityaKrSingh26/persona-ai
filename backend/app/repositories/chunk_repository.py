import uuid

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def insert_chunks(
        self,
        source_id: uuid.UUID,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> int:
        chunk_objs = [
            Chunk(
                source_id=source_id,
                content=text_,
                embedding=embedding,
                metadata_=metadata,
                chunk_index=i,
            )
            for i, (text_, embedding) in enumerate(zip(chunks, embeddings))
        ]
        self.db.add_all(chunk_objs)
        await self.db.flush()
        return len(chunk_objs)

    async def delete_by_source(self, source_id: uuid.UUID) -> None:
        await self.db.execute(delete(Chunk).where(Chunk.source_id == source_id))
        await self.db.flush()

    async def search_similar(
        self,
        embedding: list[float],
        top_k: int,
        min_similarity: float,
    ) -> list:
        # Raw SQL — the <=> cosine distance operator is pgvector-specific syntax
        # not expressible via SQLAlchemy ORM
        result = await self.db.execute(
            text(
                """
                SELECT c.content, s.label,
                       1 - (c.embedding <=> CAST(:emb AS vector)) AS similarity
                FROM chunks c
                JOIN sources s ON c.source_id = s.id
                WHERE s.status = 'ready'
                  AND 1 - (c.embedding <=> CAST(:emb AS vector)) > :min_sim
                ORDER BY c.embedding <=> CAST(:emb AS vector)
                LIMIT :k
                """
            ),
            {
                "emb": str(embedding),
                "min_sim": min_similarity,
                "k": top_k,
            },
        )
        return result.fetchall()
