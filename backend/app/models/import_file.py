from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ImportFile(Base):
    __tablename__ = "import_files"
    __table_args__ = (
        Index("idx_import_files_polygon_uploaded", "polygon_id", "uploaded_at"),
    )

    import_file_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    polygon_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("polygons.polygon_id"), nullable=False)
    collector_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("data_collectors.collector_id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    rows_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    measurements_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    polygon = relationship("Polygon", back_populates="import_files")
    collector = relationship("DataCollector", back_populates="import_files")
    measurements = relationship("Measurement", back_populates="import_file")
