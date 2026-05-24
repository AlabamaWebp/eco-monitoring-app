from datetime import datetime

from pydantic import BaseModel


class DashboardImportItem(BaseModel):
    import_file_id: int
    file_name: str
    polygon_name: str
    collector_last_name: str
    uploaded_at: datetime
    status: str
    rows_count: int
    measurements_count: int


class DashboardSummaryResponse(BaseModel):
    polygons_count: int
    sensor_types_count: int
    measurements_count: int
    imports_count: int
    latest_imports: list[DashboardImportItem]

