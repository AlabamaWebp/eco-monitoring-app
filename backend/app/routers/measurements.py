from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, and_, desc, func, select
from sqlalchemy.orm import Session, aliased

from app.database import get_db
from app.models import DataCollector, ImportFile, Measurement, MeasurementUnit, Polygon, SensorType
from app.schemas.measurements import MeasurementListItem, MeasurementListResponse

router = APIRouter(tags=["measurements"])


@router.get("/measurements", response_model=MeasurementListResponse)
def list_measurements(
    polygon_id: int | None = Query(None),
    sensor_type_id: int | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    collector_id: int | None = Query(None),
    import_file_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
) -> MeasurementListResponse:
    normalized_sort = sort_order.lower()
    if normalized_sort not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="sort_order должен быть 'asc' или 'desc'.")

    import_alias = aliased(ImportFile)
    collector_alias = aliased(DataCollector)

    filters = []
    if polygon_id is not None:
        filters.append(Measurement.polygon_id == polygon_id)
    if sensor_type_id is not None:
        filters.append(Measurement.sensor_type_id == sensor_type_id)
    if date_from is not None:
        filters.append(Measurement.measured_at >= date_from)
    if date_to is not None:
        filters.append(Measurement.measured_at <= date_to)
    if collector_id is not None:
        filters.append(import_alias.collector_id == collector_id)
    if import_file_id is not None:
        filters.append(Measurement.import_file_id == import_file_id)

    order_expression = Measurement.measured_at.asc() if normalized_sort == "asc" else desc(Measurement.measured_at)

    base_stmt: Select = (
        select(
            Measurement.measurement_id.label("measurement_id"),
            Measurement.measured_at.label("measured_at"),
            Measurement.polygon_id.label("polygon_id"),
            Polygon.name.label("polygon_name"),
            Measurement.sensor_type_id.label("sensor_type_id"),
            SensorType.name.label("sensor_name"),
            SensorType.code.label("sensor_code"),
            Measurement.value.label("value"),
            MeasurementUnit.symbol.label("unit_symbol"),
            Measurement.import_file_id.label("import_file_id"),
            import_alias.file_name.label("file_name"),
            collector_alias.last_name.label("collector_last_name"),
        )
        .join(Polygon, Polygon.polygon_id == Measurement.polygon_id)
        .join(SensorType, SensorType.sensor_type_id == Measurement.sensor_type_id)
        .join(MeasurementUnit, MeasurementUnit.unit_id == Measurement.unit_id)
        .outerjoin(import_alias, import_alias.import_file_id == Measurement.import_file_id)
        .outerjoin(collector_alias, collector_alias.collector_id == import_alias.collector_id)
    )

    if filters:
        base_stmt = base_stmt.where(and_(*filters))

    count_stmt = (
        select(func.count(Measurement.measurement_id))
        .outerjoin(import_alias, import_alias.import_file_id == Measurement.import_file_id)
    )
    if filters:
        count_stmt = count_stmt.where(and_(*filters))

    total = db.scalar(count_stmt) or 0

    rows = db.execute(base_stmt.order_by(order_expression).limit(limit).offset(offset)).mappings().all()
    items = [
        MeasurementListItem(
            measurement_id=row["measurement_id"],
            measured_at=row["measured_at"],
            polygon_id=row["polygon_id"],
            polygon_name=row["polygon_name"],
            sensor_type_id=row["sensor_type_id"],
            sensor_name=row["sensor_name"],
            sensor_code=row["sensor_code"],
            value=row["value"],
            unit_symbol=row["unit_symbol"],
            import_file_id=row["import_file_id"],
            file_name=row["file_name"],
            collector_last_name=row["collector_last_name"],
        )
        for row in rows
    ]

    return MeasurementListResponse(items=items, total=int(total), limit=limit, offset=offset)
