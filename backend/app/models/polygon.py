from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import BIGINT_SQL_TYPE


class Polygon(Base):
    __tablename__ = "polygons"

    polygon_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    measurements = relationship("Measurement", back_populates="polygon")
    import_files = relationship("ImportFile", back_populates="polygon")
