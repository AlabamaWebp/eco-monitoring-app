from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement, Polygon, SensorType
from app.schemas.charts import ChartResponse, ChartSeries

router = APIRouter(tags=["charts"])

ALLOWED_AGGREGATIONS = {"raw", "hourly", "daily"}
ALLOWED_PERIODS = {"last_24h", "last_7d", "last_month"}


def _parse_id_list(raw_ids: str, field_name: str) -> list[int]:
    try:
        values = [int(value.strip()) for value in raw_ids.split(",") if value.strip()]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{field_name} должен содержать список id.") from exc
    if not values:
        raise HTTPException(status_code=400, detail=f"{field_name} не должен быть пустым.")
    return values


def _resolve_date_range(
    date_from: datetime | None,
    date_to: datetime | None,
    period: str | None,
) -> tuple[datetime | None, datetime | None]:
    if period and period not in ALLOWED_PERIODS:
        raise HTTPException(status_code=400, detail="period должен быть last_24h, last_7d или last_month.")

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from не может быть больше date_to.")

    if date_from or date_to:
        return date_from, date_to

    now = datetime.now()
    if period == "last_24h":
        return now - timedelta(hours=24), now
    if period == "last_7d":
        return now - timedelta(days=7), now
    if period == "last_month":
        return now - timedelta(days=30), now
    return None, None


def _bucket_expression(db: Session, aggregation: str):
    dialect = db.bind.dialect.name if db.bind is not None else "mysql"
    if aggregation == "hourly":
        if dialect == "sqlite":
            return func.strftime("%Y-%m-%d %H:00:00", Measurement.measured_at)
        return func.date_format(Measurement.measured_at, "%Y-%m-%d %H:00:00")
    if aggregation == "daily":
        if dialect == "sqlite":
            return func.strftime("%Y-%m-%d 00:00:00", Measurement.measured_at)
        return func.date_format(Measurement.measured_at, "%Y-%m-%d 00:00:00")
    return Measurement.measured_at


def _to_float(value: Decimal | float | int) -> float:
    return float(value)


@router.get("/charts/multi-sensor", response_model=ChartResponse)
def multi_sensor_chart(
    polygon_id: int = Query(...),
    sensor_type_ids: str = Query(...),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    period: str | None = Query(None),
    aggregation: str = Query("raw"),
    db: Session = Depends(get_db),
) -> ChartResponse:
    if aggregation not in ALLOWED_AGGREGATIONS:
        raise HTTPException(status_code=400, detail="aggregation должен быть raw, hourly или daily.")

    sensor_ids = _parse_id_list(sensor_type_ids, "sensor_type_ids")
    resolved_from, resolved_to = _resolve_date_range(date_from, date_to, period)

    bucket = _bucket_expression(db, aggregation).label("bucket")
    value_expr = Measurement.value if aggregation == "raw" else func.avg(Measurement.value)

    stmt = (
        select(
            SensorType.sensor_type_id.label("sensor_type_id"),
            SensorType.name.label("sensor_name"),
            bucket,
            value_expr.label("value"),
        )
        .join(SensorType, SensorType.sensor_type_id == Measurement.sensor_type_id)
        .where(and_(Measurement.polygon_id == polygon_id, Measurement.sensor_type_id.in_(sensor_ids)))
    )
    if resolved_from is not None:
        stmt = stmt.where(Measurement.measured_at >= resolved_from)
    if resolved_to is not None:
        stmt = stmt.where(Measurement.measured_at <= resolved_to)

    if aggregation != "raw":
        stmt = stmt.group_by(SensorType.sensor_type_id, SensorType.name, bucket)

    stmt = stmt.order_by(bucket.asc(), SensorType.sensor_type_id.asc())
    rows = db.execute(stmt).mappings().all()

    sensors = {
        sensor.sensor_type_id: sensor
        for sensor in db.scalars(select(SensorType).where(SensorType.sensor_type_id.in_(sensor_ids))).all()
    }
    missing_sensor_ids = [sensor_id for sensor_id in sensor_ids if sensor_id not in sensors]
    if missing_sensor_ids:
        raise HTTPException(status_code=404, detail=f"Не найдены датчики с id: {', '.join(str(v) for v in missing_sensor_ids)}")

    series_map: dict[int, ChartSeries] = {
        sensor_id: ChartSeries(name=sensors[sensor_id].name, unit=sensors[sensor_id].unit.symbol, data=[])
        for sensor_id in sensors
    }

    for row in rows:
        sensor_id = int(row["sensor_type_id"])
        bucket_value = row["bucket"]
        timestamp = bucket_value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(bucket_value, datetime) else str(bucket_value)
        series_map[sensor_id].data.append([timestamp, _to_float(row["value"])])

    return ChartResponse(series=list(series_map.values()))


@router.get("/charts/multi-polygon", response_model=ChartResponse)
def multi_polygon_chart(
    sensor_type_id: int = Query(...),
    polygon_ids: str = Query(...),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    period: str | None = Query(None),
    aggregation: str = Query("raw"),
    db: Session = Depends(get_db),
) -> ChartResponse:
    if aggregation not in ALLOWED_AGGREGATIONS:
        raise HTTPException(status_code=400, detail="aggregation должен быть raw, hourly или daily.")

    polygon_id_list = _parse_id_list(polygon_ids, "polygon_ids")
    resolved_from, resolved_to = _resolve_date_range(date_from, date_to, period)

    sensor = db.get(SensorType, sensor_type_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail=f"Датчик с id={sensor_type_id} не найден.")

    bucket = _bucket_expression(db, aggregation).label("bucket")
    value_expr = Measurement.value if aggregation == "raw" else func.avg(Measurement.value)

    stmt = (
        select(
            Polygon.polygon_id.label("polygon_id"),
            Polygon.name.label("polygon_name"),
            bucket,
            value_expr.label("value"),
        )
        .join(Polygon, Polygon.polygon_id == Measurement.polygon_id)
        .where(and_(Measurement.sensor_type_id == sensor_type_id, Measurement.polygon_id.in_(polygon_id_list)))
    )
    if resolved_from is not None:
        stmt = stmt.where(Measurement.measured_at >= resolved_from)
    if resolved_to is not None:
        stmt = stmt.where(Measurement.measured_at <= resolved_to)

    if aggregation != "raw":
        stmt = stmt.group_by(Polygon.polygon_id, Polygon.name, bucket)

    stmt = stmt.order_by(bucket.asc(), Polygon.polygon_id.asc())
    rows = db.execute(stmt).mappings().all()

    polygons = {
        polygon.polygon_id: polygon
        for polygon in db.scalars(select(Polygon).where(Polygon.polygon_id.in_(polygon_id_list))).all()
    }
    missing_polygon_ids = [polygon_id for polygon_id in polygon_id_list if polygon_id not in polygons]
    if missing_polygon_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Не найдены полигоны с id: {', '.join(str(v) for v in missing_polygon_ids)}",
        )

    series_map: dict[int, ChartSeries] = {
        polygon_id: ChartSeries(name=polygons[polygon_id].name, unit=sensor.unit.symbol, data=[])
        for polygon_id in polygons
    }

    for row in rows:
        polygon_id = int(row["polygon_id"])
        bucket_value = row["bucket"]
        timestamp = bucket_value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(bucket_value, datetime) else str(bucket_value)
        series_map[polygon_id].data.append([timestamp, _to_float(row["value"])])

    return ChartResponse(series=list(series_map.values()))
