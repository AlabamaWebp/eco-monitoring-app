from sqlalchemy import func, select

from app.models import ImportFile, Measurement, SensorType


def _import_csv(client, payload: bytes, polygon_id: int = 1, last_name: str = "Ivanov"):
    return client.post(
        "/api/imports/csv",
        files={"file": ("polygon_1_measurements.csv", payload, "text/csv")},
        data={"polygon_id": str(polygon_id), "collector_last_name": last_name},
    )


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_reference_endpoints(client, seeded_db):
    polygons = client.get("/api/polygons")
    sensor_types = client.get("/api/sensor-types")
    units = client.get("/api/measurement-units")

    assert polygons.status_code == 200
    assert sensor_types.status_code == 200
    assert units.status_code == 200
    assert len(polygons.json()) == 3
    assert len(sensor_types.json()) == 6
    assert len(units.json()) == 6


def test_csv_import_measurements_and_skips(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность,Температура,Давление,Освещённость,Уровень шума\n"
        "2025-01-01 00:00:00,420,61,22.4,1012,450,38\n"
        "2025-01-01 01:00:00,427,,22.1,1011,430,39\n"
        "2025-01-01 02:00:00,bad,63,22.0,1010,420,40\n"
    ).encode("utf-8")

    response = _import_csv(client, csv_data)
    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "processed"
    assert body["rows_count"] == 3
    assert body["measurements_count"] == 16
    assert body["skipped_values"] == 2

    import_id = body["import_file_id"]
    import_file = seeded_db.get(ImportFile, import_id)
    assert import_file is not None
    assert import_file.status == "processed"
    assert import_file.rows_count == 3
    assert import_file.measurements_count == 16

    measurement_count = seeded_db.scalar(
        select(func.count(Measurement.measurement_id)).where(Measurement.import_file_id == import_id)
    )
    assert measurement_count == 16


def test_csv_import_fails_without_date_column(client, seeded_db):
    csv_data = (
        "CO2,Влажность,Температура\n"
        "420,61,22.4\n"
        "430,63,22.8\n"
    ).encode("utf-8")
    response = _import_csv(client, csv_data)
    assert response.status_code == 400
    assert "Дата" in response.json()["detail"]


def test_measurements_filters_and_sort(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность\n"
        "2025-01-01 00:00:00,420,61\n"
        "2025-01-01 01:00:00,430,63\n"
    ).encode("utf-8")
    imported = _import_csv(client, csv_data)
    assert imported.status_code == 200
    import_id = imported.json()["import_file_id"]

    sensor_rows = seeded_db.scalars(select(SensorType).where(SensorType.code == "co2")).all()
    co2_id = sensor_rows[0].sensor_type_id

    response = client.get(
        "/api/measurements",
        params={
            "import_file_id": import_id,
            "sensor_type_id": co2_id,
            "date_from": "2025-01-01T00:00:00",
            "date_to": "2025-01-01T01:00:00",
            "sort_order": "asc",
            "limit": 10,
            "offset": 0,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["measured_at"] <= body["items"][1]["measured_at"]


def test_dashboard_summary(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность\n"
        "2025-01-01 00:00:00,420,61\n"
    ).encode("utf-8")
    imported = _import_csv(client, csv_data)
    assert imported.status_code == 200

    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["polygons_count"] >= 3
    assert body["sensor_types_count"] >= 6
    assert body["imports_count"] >= 1
    assert len(body["latest_imports"]) >= 1


def test_chart_endpoints_return_series(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность\n"
        "2025-01-01 00:00:00,420,61\n"
        "2025-01-01 01:00:00,430,63\n"
    ).encode("utf-8")
    imported = _import_csv(client, csv_data)
    assert imported.status_code == 200

    sensors = seeded_db.scalars(select(SensorType).where(SensorType.code.in_(["co2", "humidity"]))).all()
    co2_id = next(item.sensor_type_id for item in sensors if item.code == "co2")
    humidity_id = next(item.sensor_type_id for item in sensors if item.code == "humidity")

    multi_sensor = client.get(
        "/api/charts/multi-sensor",
        params={
            "polygon_id": 1,
            "sensor_type_ids": f"{co2_id},{humidity_id}",
            "date_from": "2025-01-01T00:00:00",
            "date_to": "2025-01-01T02:00:00",
            "aggregation": "raw",
        },
    )
    assert multi_sensor.status_code == 200
    multi_sensor_body = multi_sensor.json()
    assert len(multi_sensor_body["series"]) == 2
    assert any(series["data"] for series in multi_sensor_body["series"])

    multi_polygon = client.get(
        "/api/charts/multi-polygon",
        params={
            "sensor_type_id": humidity_id,
            "polygon_ids": "1,2,3",
            "date_from": "2025-01-01T00:00:00",
            "date_to": "2025-01-01T02:00:00",
            "aggregation": "raw",
        },
    )
    assert multi_polygon.status_code == 200
    multi_polygon_body = multi_polygon.json()
    assert len(multi_polygon_body["series"]) == 3
