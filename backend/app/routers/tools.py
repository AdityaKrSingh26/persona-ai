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
    get_message_repo,
    get_session_repo,
)
from app.dependencies.vapi_auth import require_vapi_secret
from app.integrations.cal import create_booking, get_available_slots
from app.integrations.embeddings_api import EmbeddingsClient
from app.integrations.github import GitHubClient
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.schemas import (
    AppointmentRequest,
    ContactMessageRequest,
    GitHubRequest,
    SlotCheckRequest,
)

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
    message_val = body.get("message")
    if isinstance(message_val, dict):
        tool_call = (message_val.get("toolCallList") or [{}])[0]
        if tool_call:
            tool_call_id = tool_call.get("id", "unknown")
            args = tool_call.get("function", {}).get("arguments", {})
            return tool_call_id, args

    # Vapi test UI or flat payload sends a flat body — treat the whole body as args
    return "unknown", body


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

    try:
        profile = await gh_client.fetch_profile()
        total_repos = profile.get("public_repos", 0)
    except Exception:
        logger.exception("[tools] github failed to fetch profile")
        total_repos = 0

    # Clean the query
    q_clean = (query or "").strip().lower()
    is_general = q_clean in ["", "all", "repos", "repositories", "list", "github", "none"]

    if is_general:
        repos = await gh_client.fetch_repos(query=None, limit=100)
        if not repos:
            res = _vapi_result(tool_call_id, f"Total public repositories: {total_repos}. No repositories found.")
            logger.info("[tools] github response: %r", res)
            return res
        
        repo_names = [r["name"] for r in repos]
        res = _vapi_result(
            tool_call_id,
            f"Total public repositories: {total_repos}. Here are the names of all public repositories: "
            f"{', '.join(repo_names)}. Please ask about any specific repository name if you want to know its details."
        )
        logger.info("[tools] github response: %r", res)
        return res

    repos = await gh_client.fetch_repos(query=query, limit=100)
    if not repos:
        prefix = f"Total public repositories: {total_repos}. " if total_repos > 0 else ""
        res = _vapi_result(tool_call_id, f"{prefix}No repositories found matching '{query}'. The name may have been misheard. Could you try repeating or spelling the repository name?")
        logger.info("[tools] github response: %r", res)
        return res

    lines = [
        f"{r['name']}: {r.get('description') or 'No description'} ({r.get('language') or 'N/A'}) stars:{r.get('stars') or 0}"
        for r in repos
    ]
    prefix = f"Total public repositories: {total_repos}. Here are matching repositories: " if total_repos > 0 else "Here are matching repositories: "
    res = _vapi_result(tool_call_id, prefix + " | ".join(lines))
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


def _format_slots(slots_data: dict, target_tz_str: str) -> str:
    """Format available slots into a concise, voice-friendly summary.

    Instead of listing every single 30-minute slot (which can be 28+),
    this returns a short summary with the total count, a handful of
    representative times spread across the day, and the overall range.
    This prevents Vapi's LLM from being overwhelmed and skipping the
    times in its spoken response.
    """
    from zoneinfo import ZoneInfo
    from app.integrations.cal import _normalize_tz
    iana_tz = _normalize_tz(target_tz_str)

    try:
        tz = ZoneInfo(iana_tz)
    except Exception:
        tz = ZoneInfo("Asia/Kolkata")

    formatted = []
    data = slots_data.get("data", {})
    for day, slots in data.items():
        if not slots:
            continue
        day_slots = []
        for slot in slots:
            start_str = slot.get("start")
            if not start_str:
                continue
            dt_utc = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(tz)
            time_str = dt_local.strftime("%I:%M %p").lstrip("0")
            day_slots.append(time_str)

        if not day_slots:
            continue

        try:
            day_dt = datetime.strptime(day, "%Y-%m-%d")
            day_name = day_dt.strftime("%A, %B %d")
        except Exception:
            day_name = day

        total = len(day_slots)

        if total <= 6:
            # Few enough to list them all
            times_joined = ", ".join(day_slots[:-1]) + (", and " + day_slots[-1] if total > 1 else day_slots[0])
            formatted.append(f"On {day_name}, available times are: {times_joined}.")
        else:
            # Pick ~5 representative slots spread across the day
            sample_indices = [
                0,                      # earliest
                total // 4,             # ~25%
                total // 2,             # midday
                3 * total // 4,         # ~75%
                total - 1,              # latest
            ]
            # Deduplicate while preserving order
            seen = set()
            samples = []
            for i in sample_indices:
                if i not in seen:
                    seen.add(i)
                    samples.append(day_slots[i])
            sample_text = ", ".join(samples[:-1]) + ", and " + samples[-1]
            formatted.append(
                f"On {day_name}, there are {total} available slots "
                f"ranging from {day_slots[0]} to {day_slots[-1]}. "
                f"Some options include {sample_text}. "
                f"Slots are available in 30-minute increments."
            )

    if not formatted:
        return "No slots are available on this date."

    return " ".join(formatted)


@router.post("/slots")
async def tool_slots(
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
):
    logger.info("[tools] slots request headers: %r", dict(request.headers))
    logger.info("[tools] slots request body: %r", body)
    tool_call_id, args = _parse_vapi_body(body)

    date_str = args.get("date")
    timezone_str = args.get("timezone", "Asia/Kolkata")

    logger.info("[tools] slots | id=%s date=%s tz=%s", tool_call_id, date_str, timezone_str)

    if not date_str:
        res = _vapi_error(tool_call_id, "No date provided.")
        logger.info("[tools] slots response: %r", res)
        return res

    try:
        req = SlotCheckRequest(**args)
        
        from app.integrations.cal import _normalize_tz
        iana_tz = _normalize_tz(req.timezone)
        
        if "T" in req.date:
            date_clean = req.date.split("T")[0]
        else:
            date_clean = req.date
            
        start_date = f"{date_clean}T00:00:00Z"
        end_date = f"{date_clean}T23:59:59Z"
        
        slots_data = await get_available_slots(start_date, end_date, req.timezone)
        formatted_message = _format_slots(slots_data, req.timezone)
        
        res = _vapi_result(tool_call_id, formatted_message)
        logger.info("[tools] slots response: %r", res)
        return res
    except Exception as e:
        logger.exception("[tools] slots failed | id=%s", tool_call_id)
        res = _vapi_error(tool_call_id, f"Failed to check slots: {e}")
        logger.info("[tools] slots response: %r", res)
        return res


@router.post("/contact")
async def tool_contact(
    request: Request,
    body: dict,
    _: None = Depends(require_vapi_secret),
    db: AsyncSession = Depends(get_db),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    logger.info("[tools] contact request headers: %r", dict(request.headers))
    logger.info("[tools] contact request body: %r", body)
    tool_call_id, args = _parse_vapi_body(body)

    visitor_name = args.get("visitor_name")
    visitor_email = args.get("visitor_email")
    message = args.get("message")

    logger.info("[tools] contact | id=%s visitor=%s email=%s", tool_call_id, visitor_name, visitor_email)

    if not visitor_name or not visitor_email or not message:
        res = _vapi_error(tool_call_id, "Missing visitor name, email, or message.")
        logger.info("[tools] contact response: %r", res)
        return res

    try:
        req = ContactMessageRequest(**args)
        await message_repo.create(
            visitor_name=req.visitor_name,
            visitor_email=str(req.visitor_email),
            message=req.message,
        )
        await db.commit()
        res = _vapi_result(
            tool_call_id,
            f"Message saved successfully! I have let Aditya know, and he will get back to you at {req.visitor_email}."
        )
        logger.info("[tools] contact response: %r", res)
        return res
    except Exception as e:
        logger.exception("[tools] contact failed | id=%s", tool_call_id)
        res = _vapi_error(tool_call_id, f"Failed to save message: {e}")
        logger.info("[tools] contact response: %r", res)
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

