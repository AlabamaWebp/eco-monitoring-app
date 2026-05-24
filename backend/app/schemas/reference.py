from pydantic import BaseModel


class PolygonRead(BaseModel):
    polygon_id: int
    name: str
    location: str | None
    description: str | None


class MeasurementUnitRead(BaseModel):
    unit_id: int
    name: str
    symbol: str
    description: str | None


class SensorTypeRead(BaseModel):
    sensor_type_id: int
    unit_id: int
    name: str
    code: str
    description: str | None
    unit_symbol: str

