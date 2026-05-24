from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImportFile, Measurement, Polygon, SensorType
from app.schemas.dashboard import DashboardImportItem, DashboardSummaryResponse

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryResponse:
    polygons_count = db.scalar(select(func.count(Polygon.polygon_id))) or 0
    sensor_types_count = db.scalar(select(func.count(SensorType.sensor_type_id))) or 0
    measurements_count = db.scalar(select(func.count(Measurement.measurement_id))) or 0
    imports_count = db.scalar(select(func.count(ImportFile.import_file_id))) or 0

    latest_import_entities = db.scalars(
        select(ImportFile).order_by(ImportFile.uploaded_at.desc()).limit(5)
    ).all()
    latest_imports = [
        DashboardImportItem(
            import_file_id=item.import_file_id,
            file_name=item.file_name,
            polygon_name=item.polygon.name,
            collector_last_name=item.collector.last_name,
            uploaded_at=item.uploaded_at,
            status=item.status,
            rows_count=item.rows_count,
            measurements_count=item.measurements_count,
        )
        for item in latest_import_entities
    ]

    return DashboardSummaryResponse(
        polygons_count=int(polygons_count),
        sensor_types_count=int(sensor_types_count),
        measurements_count=int(measurements_count),
        imports_count=int(imports_count),
        latest_imports=latest_imports,
    )

