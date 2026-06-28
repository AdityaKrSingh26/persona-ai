import hmac

from fastapi import Header, HTTPException

from app.config import settings


def require_vapi_secret(x_vapi_secret: str = Header(...)) -> None:
    # Both sides encoded to bytes — hmac.compare_digest requires matching types
    if not hmac.compare_digest(
        x_vapi_secret.encode("utf-8"),
        settings.vapi_server_secret.encode("utf-8"),
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
