from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models import ImportFile, Measurement, MeasurementUnit, Polygon, SensorType
from app.schemas.reference import MeasurementUnitWrite, PolygonWrite, SensorTypeWrite


def create_polygon(db: Session, payload: PolygonWrite) -> Polygon:
    polygon = Polygon(
        name=payload.name,
        location=payload.location,
        description=payload.description,
    )
    db.add(polygon)
    db.commit()
    db.refresh(polygon)
    return polygon


def update_polygon(db: Session, polygon_id: int, payload: PolygonWrite) -> Polygon:
    polygon = db.get(Polygon, polygon_id)
    if polygon is None:
        raise HTTPException(status_code=404, detail="Полигон не найден.")

    polygon.name = payload.name
    polygon.location = payload.location
    polygon.description = payload.description
    db.commit()
    db.refresh(polygon)
    return polygon


def delete_polygon(db: Session, polygon_id: int) -> None:
    polygon = db.get(Polygon, polygon_id)
    if polygon is None:
        raise HTTPException(status_code=404, detail="Полигон не найден.")

    has_measurements = bool(
        db.scalar(select(func.count(Measurement.measurement_id)).where(Measurement.polygon_id == polygon_id)) or 0
    )
    has_imports = bool(
        db.scalar(select(func.count(ImportFile.import_file_id)).where(ImportFile.polygon_id == polygon_id)) or 0
    )
    if has_measurements or has_imports:
        raise HTTPException(
            status_code=409,
            detail="Невозможно удалить полигон: существуют связанные измерения или загрузки файлов.",
        )

    db.delete(polygon)
    db.commit()


def create_measurement_unit(db: Session, payload: MeasurementUnitWrite) -> MeasurementUnit:
    existing = db.scalar(select(MeasurementUnit).where(func.lower(MeasurementUnit.symbol) == payload.symbol.lower()))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Единица измерения с таким обозначением уже существует.")

    unit = MeasurementUnit(
        name=payload.name,
        symbol=payload.symbol,
        description=payload.description,
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def update_measurement_unit(db: Session, unit_id: int, payload: MeasurementUnitWrite) -> MeasurementUnit:
    unit = db.get(MeasurementUnit, unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="Единица измерения не найдена.")

    duplicate = db.scalar(
        select(MeasurementUnit).where(
            func.lower(MeasurementUnit.symbol) == payload.symbol.lower(),
            MeasurementUnit.unit_id != unit_id,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="Единица измерения с таким обозначением уже существует.")

    unit.name = payload.name
    unit.symbol = payload.symbol
    unit.description = payload.description
    db.commit()
    db.refresh(unit)
    return unit


def delete_measurement_unit(db: Session, unit_id: int) -> None:
    unit = db.get(MeasurementUnit, unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="Единица измерения не найдена.")

    has_sensor_types = bool(
        db.scalar(select(func.count(SensorType.sensor_type_id)).where(SensorType.unit_id == unit_id)) or 0
    )
    has_measurements = bool(
        db.scalar(select(func.count(Measurement.measurement_id)).where(Measurement.unit_id == unit_id)) or 0
    )
    if has_sensor_types or has_measurements:
        raise HTTPException(
            status_code=409,
            detail="Невозможно удалить единицу измерения: она используется в существующих данных.",
        )

    db.delete(unit)
    db.commit()


def create_sensor_type(db: Session, payload: SensorTypeWrite) -> SensorType:
    unit = db.get(MeasurementUnit, payload.unit_id)
    if unit is None:
        raise HTTPException(status_code=400, detail="Единица измерения не найдена.")

    existing = db.scalar(select(SensorType).where(func.lower(SensorType.code) == payload.code.lower()))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Тип датчика с таким кодом уже существует.")

    sensor_type = SensorType(
        unit_id=payload.unit_id,
        name=payload.name,
        code=payload.code,
        description=payload.description,
    )
    db.add(sensor_type)
    db.commit()
    db.refresh(sensor_type)
    return sensor_type


def update_sensor_type(db: Session, sensor_type_id: int, payload: SensorTypeWrite) -> SensorType:
    sensor_type = db.get(SensorType, sensor_type_id)
    if sensor_type is None:
        raise HTTPException(status_code=404, detail="Тип датчика не найден.")

    unit = db.get(MeasurementUnit, payload.unit_id)
    if unit is None:
        raise HTTPException(status_code=400, detail="Единица измерения не найдена.")

    duplicate = db.scalar(
        select(SensorType).where(
            func.lower(SensorType.code) == payload.code.lower(),
            SensorType.sensor_type_id != sensor_type_id,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="Тип датчика с таким кодом уже существует.")

    sensor_type.unit_id = payload.unit_id
    sensor_type.name = payload.name
    sensor_type.code = payload.code
    sensor_type.description = payload.description
    db.commit()
    db.refresh(sensor_type)
    return sensor_type


def delete_sensor_type(db: Session, sensor_type_id: int) -> None:
    sensor_type = db.get(SensorType, sensor_type_id)
    if sensor_type is None:
        raise HTTPException(status_code=404, detail="Тип датчика не найден.")

    has_measurements = bool(
        db.scalar(
            select(func.count(Measurement.measurement_id)).where(Measurement.sensor_type_id == sensor_type_id)
        )
        or 0
    )
    if has_measurements:
        raise HTTPException(
            status_code=409,
            detail="Невозможно удалить тип датчика: для него существуют измерения.",
        )

    db.delete(sensor_type)
    db.commit()
