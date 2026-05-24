from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MeasurementUnit, Polygon, SensorType


def seed_reference_data(db: Session) -> dict[str, int]:
    unit_map = {
        "°C": ("Градус Цельсия", "Температура воздуха"),
        "%": ("Процент", "Относительная влажность"),
        "hPa": ("Гектопаскаль", "Атмосферное давление"),
        "ppm": ("Частей на миллион", "Концентрация CO2"),
        "lx": ("Люкс", "Освещённость"),
        "dB": ("Децибел", "Уровень шума"),
    }

    sensor_map = [
        ("temperature", "Температура", "°C", "Температура воздуха"),
        ("humidity", "Влажность", "%", "Относительная влажность"),
        ("pressure", "Давление", "hPa", "Атмосферное давление"),
        ("co2", "CO2", "ppm", "Концентрация углекислого газа"),
        ("light", "Освещённость", "lx", "Уровень освещённости"),
        ("noise", "Уровень шума", "dB", "Уровень акустического шума"),
    ]

    polygons = [
        {
            "name": "Полигон №1",
            "location": "Северная зона",
            "description": "Тестовый полигон для калибровки",
            "aliases": {"Полигон №1", "Polygon #1"},
        },
        {
            "name": "Полигон №2",
            "location": "Центральная зона",
            "description": "Городской полигон мониторинга",
            "aliases": {"Полигон №2", "Polygon #2"},
        },
        {
            "name": "Полигон №3",
            "location": "Южная зона",
            "description": "Полигон в природной зоне",
            "aliases": {"Полигон №3", "Polygon #3"},
        },
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

    for item in polygons:
        exists = db.scalar(select(Polygon).where(Polygon.name.in_(item["aliases"])))
        if exists is None:
            db.add(
                Polygon(
                    name=item["name"],
                    location=item["location"],
                    description=item["description"],
                )
            )
            inserted_polygons += 1

    db.commit()
    return {"units": inserted_units, "sensor_types": inserted_sensors, "polygons": inserted_polygons}
