from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Body, Depends, HTTPException, Response

from app.database import get_db
from app.models import MeasurementUnit, Polygon, SensorType
from app.schemas.reference import (
    MeasurementUnitRead,
    MeasurementUnitWrite,
    PolygonRead,
    PolygonWrite,
    SensorTypeRead,
    SensorTypeWrite,
)
from app.services.reference_crud import (
    create_measurement_unit,
    create_polygon,
    create_sensor_type,
    delete_measurement_unit,
    delete_polygon,
    delete_sensor_type,
    update_measurement_unit,
    update_polygon,
    update_sensor_type,
)

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


@router.post("/polygons", response_model=PolygonRead, status_code=201)
def add_polygon(payload: dict = Body(...), db: Session = Depends(get_db)) -> PolygonRead:
    parsed = _parse_payload(PolygonWrite, payload)
    polygon = create_polygon(db, parsed)
    return PolygonRead(
        polygon_id=polygon.polygon_id,
        name=polygon.name,
        location=polygon.location,
        description=polygon.description,
    )


@router.put("/polygons/{polygon_id}", response_model=PolygonRead)
def edit_polygon(polygon_id: int, payload: dict = Body(...), db: Session = Depends(get_db)) -> PolygonRead:
    parsed = _parse_payload(PolygonWrite, payload)
    polygon = update_polygon(db, polygon_id, parsed)
    return PolygonRead(
        polygon_id=polygon.polygon_id,
        name=polygon.name,
        location=polygon.location,
        description=polygon.description,
    )


@router.delete("/polygons/{polygon_id}", status_code=204, response_class=Response)
def remove_polygon(polygon_id: int, db: Session = Depends(get_db)) -> Response:
    delete_polygon(db, polygon_id)
    return Response(status_code=204)


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


@router.post("/measurement-units", response_model=MeasurementUnitRead, status_code=201)
def add_measurement_unit(payload: dict = Body(...), db: Session = Depends(get_db)) -> MeasurementUnitRead:
    parsed = _parse_payload(MeasurementUnitWrite, payload)
    unit = create_measurement_unit(db, parsed)
    return MeasurementUnitRead(
        unit_id=unit.unit_id,
        name=unit.name,
        symbol=unit.symbol,
        description=unit.description,
    )


@router.put("/measurement-units/{unit_id}", response_model=MeasurementUnitRead)
def edit_measurement_unit(unit_id: int, payload: dict = Body(...), db: Session = Depends(get_db)) -> MeasurementUnitRead:
    parsed = _parse_payload(MeasurementUnitWrite, payload)
    unit = update_measurement_unit(db, unit_id, parsed)
    return MeasurementUnitRead(
        unit_id=unit.unit_id,
        name=unit.name,
        symbol=unit.symbol,
        description=unit.description,
    )


@router.delete("/measurement-units/{unit_id}", status_code=204, response_class=Response)
def remove_measurement_unit(unit_id: int, db: Session = Depends(get_db)) -> Response:
    delete_measurement_unit(db, unit_id)
    return Response(status_code=204)


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


@router.post("/sensor-types", response_model=SensorTypeRead, status_code=201)
def add_sensor_type(payload: dict = Body(...), db: Session = Depends(get_db)) -> SensorTypeRead:
    parsed = _parse_payload(SensorTypeWrite, payload)
    sensor_type = create_sensor_type(db, parsed)
    return SensorTypeRead(
        sensor_type_id=sensor_type.sensor_type_id,
        unit_id=sensor_type.unit_id,
        name=sensor_type.name,
        code=sensor_type.code,
        description=sensor_type.description,
        unit_symbol=sensor_type.unit.symbol,
    )


@router.put("/sensor-types/{sensor_type_id}", response_model=SensorTypeRead)
def edit_sensor_type(sensor_type_id: int, payload: dict = Body(...), db: Session = Depends(get_db)) -> SensorTypeRead:
    parsed = _parse_payload(SensorTypeWrite, payload)
    sensor_type = update_sensor_type(db, sensor_type_id, parsed)
    return SensorTypeRead(
        sensor_type_id=sensor_type.sensor_type_id,
        unit_id=sensor_type.unit_id,
        name=sensor_type.name,
        code=sensor_type.code,
        description=sensor_type.description,
        unit_symbol=sensor_type.unit.symbol,
    )


@router.delete("/sensor-types/{sensor_type_id}", status_code=204, response_class=Response)
def remove_sensor_type(sensor_type_id: int, db: Session = Depends(get_db)) -> Response:
    delete_sensor_type(db, sensor_type_id)
    return Response(status_code=204)


def _parse_payload(schema_model: type, payload: dict):
    try:
        return schema_model.model_validate(payload)
    except ValidationError as exc:
        errors = exc.errors()
        detail = errors[0]["msg"] if errors else "Некорректные данные формы."
        raise HTTPException(status_code=400, detail=detail) from exc
