from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import BIGINT_SQL_TYPE


class MeasurementUnit(Base):
    __tablename__ = "measurement_units"

    unit_id: Mapped[int] = mapped_column(BIGINT_SQL_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sensor_types = relationship("SensorType", back_populates="unit")
    measurements = relationship("Measurement", back_populates="unit")
