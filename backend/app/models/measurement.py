from decimal import Decimal
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import BIGINT_SQL_TYPE


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        Index("idx_measurements_polygon_sensor_time", "polygon_id", "sensor_type_id", "measured_at"),
        Index("idx_measurements_sensor_time_polygon", "sensor_type_id", "measured_at", "polygon_id"),
        Index("idx_measurements_time", "measured_at"),
        Index("idx_measurements_import_file", "import_file_id"),
    )

    measurement_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, primary_key=True, autoincrement=True)
    polygon_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, ForeignKey("polygons.polygon_id"), nullable=False)
    sensor_type_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, ForeignKey("sensor_types.sensor_type_id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, ForeignKey("measurement_units.unit_id"), nullable=False)
    import_file_id: Mapped[int | None] = mapped_column(
        BIGINT_SQL_TYPE, ForeignKey("import_files.import_file_id"), nullable=True
    )
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    polygon = relationship("Polygon", back_populates="measurements")
    sensor_type = relationship("SensorType", back_populates="measurements")
    unit = relationship("MeasurementUnit", back_populates="measurements")
    import_file = relationship("ImportFile", back_populates="measurements")
