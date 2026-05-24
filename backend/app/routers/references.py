from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.database import get_db
from app.models import MeasurementUnit, Polygon, SensorType
from app.schemas.reference import MeasurementUnitRead, PolygonRead, SensorTypeRead

router = APIRouter(tags=["references"])


@router.get("/polygons", response_model=list[PolygonRead])
def list_polygons(db: Session = Depends(get_db)) -> list[PolygonRead]:
    polygons = db.scalars(select(Polygon).order_by(Polygon.name.asc())).all()
    return [
        PolygonRead(
            polygon_id=item.polygon_id,
            name=item.name,
            location=item.location,
            description=item.description,
        )
        for item in polygons
    ]


@router.get("/measurement-units", response_model=list[MeasurementUnitRead])
def list_measurement_units(db: Session = Depends(get_db)) -> list[MeasurementUnitRead]:
    units = db.scalars(select(MeasurementUnit).order_by(MeasurementUnit.name.asc())).all()
    return [
        MeasurementUnitRead(
            unit_id=item.unit_id,
            name=item.name,
            symbol=item.symbol,
            description=item.description,
        )
        for item in units
    ]


@router.get("/sensor-types", response_model=list[SensorTypeRead])
def list_sensor_types(db: Session = Depends(get_db)) -> list[SensorTypeRead]:
    sensor_types = db.scalars(select(SensorType).order_by(SensorType.name.asc())).all()
    return [
        SensorTypeRead(
            sensor_type_id=item.sensor_type_id,
            unit_id=item.unit_id,
            name=item.name,
            code=item.code,
            description=item.description,
            unit_symbol=item.unit.symbol,
        )
        for item in sensor_types
    ]

