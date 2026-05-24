import re

from sqlalchemy import select

from app.database import SessionLocal
from app.models import DataCollector, MeasurementUnit, Polygon, SensorType


def _localize_units(session) -> int:
    updated = 0

    symbol_aliases = {"В°C": "°C"}
    for old_symbol, new_symbol in symbol_aliases.items():
        unit = session.scalar(select(MeasurementUnit).where(MeasurementUnit.symbol == old_symbol))
        if unit:
            unit.symbol = new_symbol
            updated += 1

    unit_map = {
        "°C": ("Градус Цельсия", "Температура воздуха"),
        "%": ("Процент", "Относительная влажность"),
        "hPa": ("Гектопаскаль", "Атмосферное давление"),
        "ppm": ("Частей на миллион", "Концентрация CO2"),
        "lx": ("Люкс", "Освещённость"),
        "dB": ("Децибел", "Уровень шума"),
    }

    for symbol, (name, description) in unit_map.items():
        unit = session.scalar(select(MeasurementUnit).where(MeasurementUnit.symbol == symbol))
        if unit and (unit.name != name or unit.description != description):
            unit.name = name
            unit.description = description
            updated += 1

    return updated


def _localize_sensors(session) -> int:
    updated = 0
    sensor_map = {
        "temperature": ("Температура", "Температура воздуха"),
        "humidity": ("Влажность", "Относительная влажность"),
        "pressure": ("Давление", "Атмосферное давление"),
        "co2": ("CO2", "Концентрация углекислого газа"),
        "light": ("Освещённость", "Уровень освещённости"),
        "noise": ("Уровень шума", "Уровень акустического шума"),
    }

    for code, (name, description) in sensor_map.items():
        sensor = session.scalar(select(SensorType).where(SensorType.code == code))
        if sensor and (sensor.name != name or sensor.description != description):
            sensor.name = name
            sensor.description = description
            updated += 1
    return updated


def _localize_polygons(session) -> int:
    updated = 0
    polygons = session.scalars(select(Polygon)).all()

    explicit_map = {
        "Polygon #1": ("Полигон №1", "Северная зона", "Тестовый полигон для калибровки"),
        "Polygon #2": ("Полигон №2", "Центральная зона", "Городской полигон мониторинга"),
        "Polygon #3": ("Полигон №3", "Южная зона", "Полигон в природной зоне"),
    }

    for polygon in polygons:
        target = explicit_map.get(polygon.name)
        if target:
            name, location, description = target
            polygon.name = name
            polygon.location = location
            polygon.description = description
            updated += 1
            continue

        # Generic conversion for names like "Polygon #10".
        match = re.match(r"^Polygon\s*#\s*(\d+)$", polygon.name or "")
        if match:
            polygon.name = f"Полигон №{match.group(1)}"
            if not polygon.location:
                polygon.location = "Без указания зоны"
            if not polygon.description:
                polygon.description = "Экологический полигон"
            updated += 1

    return updated


def _localize_collectors(session) -> int:
    updated = 0
    translit_map = {
        "ivanov": "Иванов",
        "petrov": "Петров",
        "smirnov": "Смирнов",
        "sidorov": "Сидоров",
    }

    collectors = session.scalars(select(DataCollector)).all()
    for collector in collectors:
        if not collector.last_name:
            continue
        key = collector.last_name.strip().lower()
        new_value = translit_map.get(key)
        if new_value and collector.last_name != new_value:
            collector.last_name = new_value
            updated += 1

    return updated


def main() -> None:
    with SessionLocal() as session:
        units_updated = _localize_units(session)
        sensors_updated = _localize_sensors(session)
        polygons_updated = _localize_polygons(session)
        collectors_updated = _localize_collectors(session)
        session.commit()

    print(
        "Localization completed:",
        {
            "units_updated": units_updated,
            "sensors_updated": sensors_updated,
            "polygons_updated": polygons_updated,
            "collectors_updated": collectors_updated,
        },
    )


if __name__ == "__main__":
    main()
