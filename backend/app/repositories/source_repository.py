import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source


class SourceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[Source]:
        result = await self.db.execute(select(Source).order_by(Source.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, source_id: uuid.UUID) -> Optional[Source]:
        result = await self.db.execute(select(Source).where(Source.id == source_id))
        return result.scalar_one_or_none()

    async def get_resume(self) -> Optional[Source]:
        result = await self.db.execute(
            # limit(1) because the schema allows at most one resume but doesn't enforce it with a unique constraint
            select(Source).where(Source.type == "resume").limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        type: str,
        label: str,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        status: str = "ready",
        error: Optional[str] = None,
        chunk_count: int = 0,
        indexed_at: Optional[datetime] = None,
    ) -> Source:
        source = Source(
            type=type,
            label=label,
            url=url,
            file_path=file_path,
            status=status,
            error=error,
            chunk_count=chunk_count,
            indexed_at=indexed_at,
        )
        self.db.add(source)
        await self.db.flush()  # assigns the DB-generated UUID without committing
        return source

    async def update(self, source: Source, **kwargs) -> Source:
        for key, value in kwargs.items():
            setattr(source, key, value)
        await self.db.flush()  # caller controls commit boundary
        return source

    async def delete(self, source: Source) -> None:
        await self.db.delete(source)
        await self.db.flush()  # caller controls commit boundary
