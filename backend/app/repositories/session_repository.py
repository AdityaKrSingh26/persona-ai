from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import CallSession


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, vapi_call_id: str, metadata: Optional[dict] = None) -> CallSession:
        session = CallSession(
            vapi_call_id=vapi_call_id,
            metadata_=metadata or {},
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def update_end(
        self,
        vapi_call_id: str,
        ended_at: datetime,
        turn_count: int,
    ) -> None:
        result = await self.db.execute(
            select(CallSession).where(CallSession.vapi_call_id == vapi_call_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.ended_at = ended_at
            session.turn_count = turn_count
            await self.db.flush()
