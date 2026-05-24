from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import BIGINT_SQL_TYPE


class SensorType(Base):
    __tablename__ = "sensor_types"

    sensor_type_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, primary_key=True, autoincrement=True)
    unit_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, ForeignKey("measurement_units.unit_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    unit = relationship("MeasurementUnit", back_populates="sensor_types")
    measurements = relationship("Measurement", back_populates="sensor_type")
