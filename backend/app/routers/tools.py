import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.retrieval import retrieve
from app.db import get_db
from app.dependencies.providers import (
    get_chunk_repo,
    get_embeddings_client,
    get_github_client,
    get_session_repo,
)
from app.dependencies.vapi_auth import require_vapi_secret
from app.integrations.cal import create_booking
from app.integrations.embeddings_api import EmbeddingsClient
from app.integrations.github import GitHubClient
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.session_repository import SessionRepository
from app.schemas import AppointmentRequest, GitHubRequest

router = APIRouter(prefix="/tools", tags=["tools"])
logger = logging.getLogger(__name__)


def _vapi_result(tool_call_id: str, result: str) -> dict:
    # Vapi requires single-line strings — newlines break parsing
    return {
        "results": [
            {"toolCallId": tool_call_id, "result": result.replace("\n", " ")}
        ]
    }


def _vapi_error(tool_call_id: str, error: str) -> dict:
    return {
        "results": [
            {"toolCallId": tool_call_id, "error": error.replace("\n", " ")}
        ]
    }


def _parse_vapi_body(body: dict) -> tuple[str, dict]:
    """Return (tool_call_id, args) from either the Vapi call envelope or the flat test-UI body."""
    tool_call = (body.get("message", {}).get("toolCallList") or [{}])[0]
    if tool_call:
        tool_call_id = tool_call.get("id", "unknown")
        args = tool_call.get("function", {}).get("arguments", {})
    else:
        # Vapi test UI sends a flat body — treat the whole body as args
        tool_call_id = "unknown"
        args = body
    return tool_call_id, args


@router.post("/retrieve")
async def tool_retrieve(
    body: dict,
    _: None = Depends(require_vapi_secret),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embeddings_client: EmbeddingsClient = Depends(get_embeddings_client),
):
    tool_call_id, args = _parse_vapi_body(body)
    query = args.get("query", "")

    logger.info("[tools] retrieve | id=%s query=%r", tool_call_id, query)

    if not query:
        return _vapi_error(tool_call_id, "No query provided.")

    chunks = await retrieve(chunk_repo, embeddings_client, query, top_k=5)
    if not chunks:
        return _vapi_result(tool_call_id, "No relevant information found in the knowledge base.")

    context = " --- ".join(f"[{row.label}] {row.content}" for row in chunks)
    return _vapi_result(tool_call_id, context)


@router.post("/github")
async def tool_github(
    body: dict,
    _: None = Depends(require_vapi_secret),
    gh_client: GitHubClient = Depends(get_github_client),
):
    tool_call_id, args = _parse_vapi_body(body)
    query = args.get("query")

    logger.info("[tools] github | id=%s query=%r", tool_call_id, query)

    repos = await gh_client.fetch_repos(query=query, limit=10)
    if not repos:
        return _vapi_result(tool_call_id, "No repositories found.")

    lines = [
        f"{r['name']}: {r.get('description', 'No description')} ({r.get('language', 'N/A')}) stars:{r.get('stars', 0)}"
        for r in repos
    ]
    return _vapi_result(tool_call_id, " | ".join(lines))


@router.post("/appointment")
async def tool_appointment(
    body: dict,
    _: None = Depends(require_vapi_secret),
):
    tool_call_id, args = _parse_vapi_body(body)

    logger.info("[tools] appointment | id=%s visitor=%s", tool_call_id, args.get("visitor_name"))

    try:
        req = AppointmentRequest(**args)
        result = await create_booking(
            visitor_name=req.visitor_name,
            visitor_email=str(req.visitor_email),
            start_time=req.start_time,
            notes=req.notes,
            timezone=req.timezone,
        )
        booking_url = result.get("data", {}).get("meetingUrl") or "https://cal.com/adityakrsingh/30min"
        return _vapi_result(tool_call_id, f"Meeting booked! Join link: {booking_url}. A confirmation has been sent to {req.visitor_email}.")
    except Exception as e:
        logger.exception("[tools] appointment failed | id=%s", tool_call_id)
        return _vapi_error(tool_call_id, f"Failed to book meeting: {e}")


@router.post("/session")
async def tool_session(
    body: dict,
    _: None = Depends(require_vapi_secret),
    db: AsyncSession = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    event_type = body.get("message", {}).get("type") or body.get("type")
    call = body.get("message", {}).get("call") or body.get("call") or {}
    call_id = call.get("id")

    if not call_id:
        return {"ok": True}

    if event_type == "call-start":
        await session_repo.create(call_id, metadata=body)
        await db.commit()
        logger.info("[tools] vapi call-start | call_id=%s", call_id)

    elif event_type == "call-end":
        ended_at = datetime.now(timezone.utc)
        turn_count = call.get("turn_count", 0)
        await session_repo.update_end(call_id, ended_at, turn_count)
        await db.commit()
        logger.info("[tools] vapi call-end | call_id=%s turns=%d", call_id, turn_count)

    else:
        logger.debug("[tools] vapi event ignored | type=%s call_id=%s", event_type, call_id)

    return {"ok": True}
