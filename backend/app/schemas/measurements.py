from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeasurementWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    polygon_id: int = Field(gt=0)
    sensor_type_id: int = Field(gt=0)
    measured_at: datetime
    value: Decimal
    collector_last_name: str | None = None

    @field_validator("collector_last_name")
    @classmethod
    def normalize_collector_last_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Фамилия не может быть пустой.")
        return normalized


class MeasurementWriteResponse(BaseModel):
    measurement_id: int


class MeasurementListItem(BaseModel):
    measurement_id: int
    measured_at: datetime
    polygon_id: int
    polygon_name: str
    sensor_type_id: int
    sensor_name: str
    sensor_code: str
    value: Decimal
    unit_symbol: str
    import_file_id: int | None
    file_name: str | None
    collector_last_name: str | None


class MeasurementListResponse(BaseModel):
    items: list[MeasurementListItem]
    total: int
    limit: int
    offset: int
