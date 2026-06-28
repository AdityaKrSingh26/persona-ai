from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.chunk import Chunk


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str]
    label: Mapped[str]
    url: Mapped[Optional[str]] = mapped_column(nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="ready")
    error: Mapped[Optional[str]] = mapped_column(nullable=True)
    chunk_count: Mapped[int] = mapped_column(default=0)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())

    chunks: Mapped[list[Chunk]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="select",
    )
