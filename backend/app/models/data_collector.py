from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DataCollector(Base):
    __tablename__ = "data_collectors"

    collector_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    import_files = relationship("ImportFile", back_populates="collector")
