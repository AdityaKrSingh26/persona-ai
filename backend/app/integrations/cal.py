import httpx

from app.config import settings

CAL_API_BASE = "https://api.cal.com/v2"
CAL_API_VERSION = "2026-02-25"

# Map common abbreviations to IANA timezone names
_TZ_MAP = {
    "IST": "Asia/Kolkata",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "GMT": "Europe/London",
    "UTC": "UTC",
    "BST": "Europe/London",
    "CET": "Europe/Paris",
}


def _normalize_tz(tz: str) -> str:
    return _TZ_MAP.get(tz.upper(), tz) if tz else "Asia/Kolkata"


async def create_booking(
    visitor_name: str,
    visitor_email: str,
    start_time: str,
    notes: str = "",
    timezone: str = "Asia/Kolkata",
) -> dict:
    """
    Create a Cal.com booking.
    start_time must be ISO 8601 UTC, e.g. "2026-07-15T09:00:00Z"
    """
    iana_tz = _normalize_tz(timezone)

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{CAL_API_BASE}/bookings",
            headers={
                "Authorization": f"Bearer {settings.cal_api_key}",
                "cal-api-version": CAL_API_VERSION,
                "Content-Type": "application/json",
            },
            json={
                "eventTypeId": settings.cal_event_type_id,
                "start": start_time,
                "attendee": {
                    "name": visitor_name,
                    "email": visitor_email,
                    "timeZone": iana_tz,
                },
                "metadata": {"notes": notes},
            },
        )
        if resp.status_code == 400:
            data = resp.json()
            msg = data.get("error", {}).get("message", "Bad request")
            if "not available" in msg.lower() or "already has booking" in msg.lower():
                raise ValueError("That time slot is not available. Please suggest a different date or time.")
            raise ValueError(msg)
        resp.raise_for_status()
        return resp.json()
