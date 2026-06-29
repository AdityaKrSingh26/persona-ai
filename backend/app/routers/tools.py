import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
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
            {"toolCallId": tool_call_id, "result": f"Error: {error.replace('\n', ' ')}"}
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
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embeddings_client: EmbeddingsClient = Depends(get_embeddings_client),
):
    logger.info("[tools] retrieve request headers: %r", dict(request.headers))
    logger.info("[tools] retrieve request body: %r", body)
    tool_call_id, args = _parse_vapi_body(body)
    query = args.get("query", "")

    logger.info("[tools] retrieve | id=%s query=%r", tool_call_id, query)

    if not query:
        res = _vapi_error(tool_call_id, "No query provided.")
        logger.info("[tools] retrieve response: %r", res)
        return res

    chunks = await retrieve(chunk_repo, embeddings_client, query, top_k=5)
    if not chunks:
        res = _vapi_result(tool_call_id, "No relevant information found in the knowledge base.")
        logger.info("[tools] retrieve response: %r", res)
        return res

    context = " --- ".join(f"[{row.label}] {row.content}" for row in chunks)
    res = _vapi_result(tool_call_id, context)
    logger.info("[tools] retrieve response: %r", res)
    return res


@router.post("/github")
async def tool_github(
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
    gh_client: GitHubClient = Depends(get_github_client),
):
    logger.info("[tools] github request headers: %r", dict(request.headers))
    logger.info("[tools] github request body: %r", body)
    tool_call_id, args = _parse_vapi_body(body)
    query = args.get("query")

    logger.info("[tools] github | id=%s query=%r", tool_call_id, query)

    repos = await gh_client.fetch_repos(query=query, limit=10)
    if not repos:
        res = _vapi_result(tool_call_id, "No repositories found.")
        logger.info("[tools] github response: %r", res)
        return res

    lines = [
        f"{r['name']}: {r.get('description', 'No description')} ({r.get('language', 'N/A')}) stars:{r.get('stars', 0)}"
        for r in repos
    ]
    res = _vapi_result(tool_call_id, " | ".join(lines))
    logger.info("[tools] github response: %r", res)
    return res


@router.post("/appointment")
async def tool_appointment(
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
):
    logger.info("[tools] appointment request headers: %r", dict(request.headers))
    logger.info("[tools] appointment request body: %r", body)
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
        res = _vapi_result(tool_call_id, f"Meeting booked! Join link: {booking_url}. A confirmation has been sent to {req.visitor_email}.")
        logger.info("[tools] appointment response: %r", res)
        return res
    except Exception as e:
        logger.exception("[tools] appointment failed | id=%s", tool_call_id)
        res = _vapi_error(tool_call_id, f"Failed to book meeting: {e}")
        logger.info("[tools] appointment response: %r", res)
        return res


@router.post("/session")
async def tool_session(
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
    db: AsyncSession = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    logger.info("[tools] session request headers: %r", dict(request.headers))
    logger.info("[tools] session request body: %r", body)
    event_type = body.get("message", {}).get("type") or body.get("type")
    call = body.get("message", {}).get("call") or body.get("call") or {}
    call_id = call.get("id")

    if not call_id:
        res = {"ok": True}
        logger.info("[tools] session response: %r", res)
        return res

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

    res = {"ok": True}
    logger.info("[tools] session response: %r", res)
    return res

