from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models import DataCollector, ImportFile, Measurement, Polygon, SensorType
from app.schemas.measurements import MeasurementWrite


def create_measurement(db: Session, payload: MeasurementWrite) -> Measurement:
    polygon = db.get(Polygon, payload.polygon_id)
    if polygon is None:
        raise HTTPException(status_code=400, detail="Полигон не найден.")

    sensor_type = db.get(SensorType, payload.sensor_type_id)
    if sensor_type is None:
        raise HTTPException(status_code=400, detail="Тип датчика не найден.")

    measurement = Measurement(
        polygon_id=payload.polygon_id,
        sensor_type_id=payload.sensor_type_id,
        unit_id=sensor_type.unit_id,
        import_file_id=None,
        measured_at=payload.measured_at,
        value=payload.value,
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


def update_measurement(db: Session, measurement_id: int, payload: MeasurementWrite) -> Measurement:
    measurement = db.get(Measurement, measurement_id)
    if measurement is None:
        raise HTTPException(status_code=404, detail="Измерение не найдено.")

    polygon = db.get(Polygon, payload.polygon_id)
    if polygon is None:
        raise HTTPException(status_code=400, detail="Полигон не найден.")

    sensor_type = db.get(SensorType, payload.sensor_type_id)
    if sensor_type is None:
        raise HTTPException(status_code=400, detail="Тип датчика не найден.")

    measurement.polygon_id = payload.polygon_id
    measurement.sensor_type_id = payload.sensor_type_id
    measurement.unit_id = sensor_type.unit_id
    measurement.measured_at = payload.measured_at
    measurement.value = payload.value

    if payload.collector_last_name is not None:
        if measurement.import_file_id is None:
            raise HTTPException(status_code=400, detail="Невозможно изменить фамилию для ручного измерения.")

        import_file = db.get(ImportFile, measurement.import_file_id)
        if import_file is None:
            raise HTTPException(status_code=400, detail="Источник импорта для измерения не найден.")

        collector = db.scalar(
            select(DataCollector).where(func.lower(DataCollector.last_name) == payload.collector_last_name.lower())
        )
        if collector is None:
            collector = DataCollector(last_name=payload.collector_last_name)
            db.add(collector)
            db.flush()

        import_file.collector_id = collector.collector_id

    db.commit()
    db.refresh(measurement)
    return measurement


def delete_measurement(db: Session, measurement_id: int) -> None:
    measurement = db.get(Measurement, measurement_id)
    if measurement is None:
        raise HTTPException(status_code=404, detail="Измерение не найдено.")

    db.delete(measurement)
    db.commit()
