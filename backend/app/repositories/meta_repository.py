from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_meta import AppMeta


class MetaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_token_version(self) -> int:
        # id == 1 is the single-row convention — no multi-tenant separation needed here
        result = await self.db.execute(select(AppMeta).where(AppMeta.id == 1))
        row = result.scalar_one_or_none()
        if row is None:
            raise RuntimeError("app_meta row missing — run migrations")
        return row.token_version

    async def bump_token_version(self) -> int:
        # Atomic increment via SQL — avoids a read-then-write race under concurrent logout
        result = await self.db.execute(
            text("UPDATE app_meta SET token_version = token_version + 1 WHERE id = 1 RETURNING token_version")
        )
        await self.db.flush()
        return result.scalar_one()
