from datetime import datetime

from pydantic import BaseModel


class ImportCsvResponse(BaseModel):
    import_file_id: int
    file_name: str
    status: str
    rows_count: int
    measurements_count: int
    skipped_values: int


class ImportListItem(BaseModel):
    import_file_id: int
    file_name: str
    polygon_name: str
    collector_last_name: str
    uploaded_at: datetime
    rows_count: int
    measurements_count: int
    status: str
    error_message: str | None

