from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MeasurementUnit, Polygon, SensorType


def seed_reference_data(db: Session) -> dict[str, int]:
    unit_map = {
        "°C": ("Degrees Celsius", "Temperature in Celsius"),
        "%": ("Percent", "Relative humidity"),
        "hPa": ("Hectopascal", "Atmospheric pressure"),
        "ppm": ("Parts per million", "CO2 concentration"),
        "lx": ("Lux", "Illuminance"),
        "dB": ("Decibel", "Sound pressure level"),
    }

    sensor_map = [
        ("temperature", "Temperature", "°C", "Air temperature"),
        ("humidity", "Humidity", "%", "Relative humidity"),
        ("pressure", "Pressure", "hPa", "Atmospheric pressure"),
        ("co2", "CO2", "ppm", "Carbon dioxide concentration"),
        ("light", "Light", "lx", "Ambient light"),
        ("noise", "Noise", "dB", "Environmental noise"),
    ]

    polygons = [
        ("Polygon #1", "North zone", "Test polygon for calibration"),
        ("Polygon #2", "Central zone", "Urban monitoring polygon"),
        ("Polygon #3", "South zone", "Reserve area polygon"),
    ]

    inserted_units = 0
    inserted_sensors = 0
    inserted_polygons = 0

    for symbol, (name, description) in unit_map.items():
        exists = db.scalar(select(MeasurementUnit).where(MeasurementUnit.symbol == symbol))
        if exists is None:
            db.add(MeasurementUnit(name=name, symbol=symbol, description=description))
            inserted_units += 1

    db.flush()
    unit_by_symbol = {unit.symbol: unit for unit in db.scalars(select(MeasurementUnit)).all()}

    for code, name, symbol, description in sensor_map:
        exists = db.scalar(select(SensorType).where(SensorType.code == code))
        if exists is None:
            db.add(
                SensorType(
                    name=name,
                    code=code,
                    description=description,
                    unit_id=unit_by_symbol[symbol].unit_id,
                )
            )
            inserted_sensors += 1

    for name, location, description in polygons:
        exists = db.scalar(select(Polygon).where(Polygon.name == name))
        if exists is None:
            db.add(Polygon(name=name, location=location, description=description))
            inserted_polygons += 1

    db.commit()
    return {"units": inserted_units, "sensor_types": inserted_sensors, "polygons": inserted_polygons}
