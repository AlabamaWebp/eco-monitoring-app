import csv
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DataCollector, ImportFile, Measurement, Polygon, SensorType

DATE_COLUMN_ALIASES = {
    "дата",
    "date",
    "datetime",
    "timestamp",
    "measured_at",
}

SENSOR_COLUMN_ALIASES = {
    "co2": "co2",
    "влажность": "humidity",
    "humidity": "humidity",
    "температура": "temperature",
    "temperature": "temperature",
    "давление": "pressure",
    "pressure": "pressure",
    "освещённость": "light",
    "освещенность": "light",
    "light": "light",
    "уровень шума": "noise",
    "noise": "noise",
}


@dataclass
class ImportResult:
    import_file_id: int
    file_name: str
    status: str
    rows_count: int
    measurements_count: int
    skipped_values: int


def _normalize_header(value: str) -> str:
    return value.strip().casefold()


def _decode_csv_bytes(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Не удалось определить кодировку CSV. Используйте UTF-8 или CP1251.")


def _parse_measured_at(raw_value: str) -> datetime:
    value = raw_value.strip()
    if not value:
        raise ValueError("Пустое значение даты.")

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    )
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Неверный формат даты: {raw_value}") from exc


def _get_or_create_collector(
    db: Session,
    last_name: str,
    first_name: str | None,
    middle_name: str | None,
) -> DataCollector:
    normalized = last_name.strip()
    if not normalized:
        raise ValueError("Фамилия загрузившего обязательна.")

    existing = db.scalar(
        select(DataCollector).where(func.lower(DataCollector.last_name) == normalized.casefold())
    )
    if existing:
        return existing

    collector = DataCollector(
        last_name=normalized,
        first_name=first_name.strip() if first_name else None,
        middle_name=middle_name.strip() if middle_name else None,
    )
    db.add(collector)
    db.commit()
    db.refresh(collector)
    return collector


def import_measurements_from_csv(
    db: Session,
    *,
    file_name: str,
    file_content: bytes,
    polygon_id: int,
    collector_last_name: str,
    collector_first_name: str | None = None,
    collector_middle_name: str | None = None,
) -> ImportResult:
    polygon = db.get(Polygon, polygon_id)
    if polygon is None:
        raise ValueError(f"Полигон с id={polygon_id} не найден.")

    collector = _get_or_create_collector(
        db,
        last_name=collector_last_name,
        first_name=collector_first_name,
        middle_name=collector_middle_name,
    )

    import_file = ImportFile(
        polygon_id=polygon.polygon_id,
        collector_id=collector.collector_id,
        file_name=file_name,
        status="uploaded",
    )
    db.add(import_file)
    db.commit()
    db.refresh(import_file)

    skipped_values = 0
    rows_count = 0
    measurements_count = 0

    try:
        decoded = _decode_csv_bytes(file_content)
        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            raise ValueError("CSV не содержит заголовок.")

        header_map = {
            original: _normalize_header(original)
            for original in reader.fieldnames
            if original is not None
        }

        date_column = next(
            (original for original, normalized in header_map.items() if normalized in DATE_COLUMN_ALIASES),
            None,
        )
        if date_column is None:
            raise ValueError("Обязательная колонка 'Дата' не найдена.")

        sensor_columns = [col for col in reader.fieldnames if col != date_column]
        if not sensor_columns:
            raise ValueError("CSV не содержит колонок датчиков.")

        sensor_types = {
            sensor.code: sensor for sensor in db.scalars(select(SensorType)).all()
        }

        resolved_columns: dict[str, SensorType] = {}
        unknown_columns: list[str] = []
        for column in sensor_columns:
            normalized = _normalize_header(column)
            sensor_code = SENSOR_COLUMN_ALIASES.get(normalized, normalized)
            sensor_type = sensor_types.get(sensor_code)
            if sensor_type is None:
                unknown_columns.append(column)
            else:
                resolved_columns[column] = sensor_type

        if unknown_columns:
            unknown = ", ".join(unknown_columns)
            raise ValueError(f"Неизвестные колонки датчиков: {unknown}")

        measurement_rows: list[Measurement] = []
        for raw_row in reader:
            rows_count += 1
            measured_at_raw = raw_row.get(date_column, "")
            measured_at = _parse_measured_at(str(measured_at_raw))

            for column, sensor_type in resolved_columns.items():
                raw_value = raw_row.get(column, "")
                if raw_value is None or str(raw_value).strip() == "":
                    skipped_values += 1
                    continue

                try:
                    value = Decimal(str(raw_value).strip())
                except InvalidOperation:
                    skipped_values += 1
                    continue

                measurement_rows.append(
                    Measurement(
                        polygon_id=polygon.polygon_id,
                        sensor_type_id=sensor_type.sensor_type_id,
                        unit_id=sensor_type.unit_id,
                        import_file_id=import_file.import_file_id,
                        measured_at=measured_at,
                        value=value,
                    )
                )

        if measurement_rows:
            db.add_all(measurement_rows)
        measurements_count = len(measurement_rows)

        import_file.rows_count = rows_count
        import_file.measurements_count = measurements_count
        import_file.status = "processed"
        import_file.error_message = None
        db.commit()
    except Exception as exc:
        db.rollback()
        import_file = db.get(ImportFile, import_file.import_file_id)
        if import_file is not None:
            import_file.rows_count = rows_count
            import_file.measurements_count = measurements_count
            import_file.status = "failed"
            import_file.error_message = str(exc)[:2000]
            db.commit()
        raise

    return ImportResult(
        import_file_id=import_file.import_file_id,
        file_name=import_file.file_name,
        status=import_file.status,
        rows_count=rows_count,
        measurements_count=measurements_count,
        skipped_values=skipped_values,
    )

