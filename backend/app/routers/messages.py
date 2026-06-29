import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies.auth import require_admin
from app.dependencies.providers import get_message_repo
from app.repositories.message_repository import MessageRepository
from app.schemas import ContactMessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[ContactMessageResponse])
async def list_messages(
    _payload: dict = Depends(require_admin),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    messages = await message_repo.list_all()
    logger.info("[messages] list all | count=%d", len(messages))
    return [ContactMessageResponse.model_validate(m) for m in messages]


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: uuid.UUID,
    _payload: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    message = await message_repo.get_by_id(message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info("[messages] delete | message_id=%s", message_id)
    await message_repo.delete(message)
    await db.commit()
    return Response(status_code=204)
