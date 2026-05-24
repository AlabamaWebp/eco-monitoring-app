from pydantic import BaseModel


class ChartPoint(BaseModel):
    timestamp: str
    value: float


class ChartSeries(BaseModel):
    name: str
    unit: str
    data: list[list[str | float]]


class ChartResponse(BaseModel):
    series: list[ChartSeries]

