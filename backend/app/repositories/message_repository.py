import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import ContactMessage


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        visitor_name: str,
        visitor_email: str,
        message: str,
    ) -> ContactMessage:
        msg = ContactMessage(
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            message=message,
        )
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def list_all(self) -> list[ContactMessage]:
        result = await self.db.execute(
            select(ContactMessage).order_by(ContactMessage.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, message_id: uuid.UUID) -> Optional[ContactMessage]:
        result = await self.db.execute(
            select(ContactMessage).where(ContactMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, message: ContactMessage) -> None:
        await self.db.delete(message)
        await self.db.flush()
