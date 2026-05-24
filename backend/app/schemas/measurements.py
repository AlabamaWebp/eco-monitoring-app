from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


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

