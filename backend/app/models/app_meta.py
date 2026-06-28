from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AppMeta(Base):
    __tablename__ = "app_meta"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_version: Mapped[int] = mapped_column(default=1)
