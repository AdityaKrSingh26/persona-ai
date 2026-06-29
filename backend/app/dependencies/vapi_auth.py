import hmac
import logging

from fastapi import Header, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


def require_vapi_secret(x_vapi_secret: str | None = Header(None)) -> None:
    logger.info("[auth] require_vapi_secret | incoming x-vapi-secret=%r", x_vapi_secret)
    if not x_vapi_secret:
        logger.warning("[auth] require_vapi_secret | rejected — missing x-vapi-secret header")
        raise HTTPException(status_code=401, detail="Missing x-vapi-secret header")

    is_valid = hmac.compare_digest(
        x_vapi_secret.encode("utf-8"),
        settings.vapi_server_secret.encode("utf-8"),
    )
    if not is_valid:
        expected_peek = settings.vapi_server_secret[:4] + "..." if settings.vapi_server_secret else ""
        received_peek = x_vapi_secret[:4] + "..." if x_vapi_secret else ""
        logger.warning(
            "[auth] require_vapi_secret | rejected — mismatch. expected=%r (len=%d) received=%r (len=%d)",
            expected_peek,
            len(settings.vapi_server_secret),
            received_peek,
            len(x_vapi_secret),
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info("[auth] require_vapi_secret | verified successfully")

