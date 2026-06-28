from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CallSession(Base):
    # Named CallSession to avoid collision with SQLAlchemy's Session class
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vapi_call_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    turn_count: Mapped[int] = mapped_column(default=0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
