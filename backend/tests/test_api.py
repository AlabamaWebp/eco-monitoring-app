from sqlalchemy import func, select

from app.models import ImportFile, Measurement, SensorType


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


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


def test_csv_import_measurements_and_charts(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность,Температура,Давление,Освещённость,Уровень шума\n"
        "2025-01-01 00:00:00,420,61,22.4,1012,450,38\n"
        "2025-01-01 01:00:00,427,,22.1,1011,430,39\n"
        "2025-01-01 02:00:00,bad,63,22.0,1010,420,40\n"
    ).encode("utf-8")

    response = client.post(
        "/api/imports/csv",
        files={"file": ("polygon_1_measurements.csv", csv_data, "text/csv")},
        data={
            "polygon_id": "1",
            "collector_last_name": "Ivanov",
        },
    )
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

    measurements_response = client.get(
        "/api/measurements",
        params={"import_file_id": import_id, "limit": 100, "offset": 0},
    )
    assert measurements_response.status_code == 200
    measurements_body = measurements_response.json()
    assert measurements_body["total"] == 16
    assert len(measurements_body["items"]) == 16
    assert measurements_body["items"][0]["polygon_name"] == "Polygon #1"

    imports_response = client.get("/api/imports")
    assert imports_response.status_code == 200
    assert imports_response.json()[0]["file_name"] == "polygon_1_measurements.csv"

    sensor_rows = seeded_db.scalars(select(SensorType).where(SensorType.code.in_(["co2", "humidity"]))).all()
    sensor_ids = sorted(item.sensor_type_id for item in sensor_rows)

    chart_multi_sensor = client.get(
        "/api/charts/multi-sensor",
        params={
            "polygon_id": 1,
            "sensor_type_ids": ",".join(str(v) for v in sensor_ids),
            "aggregation": "raw",
        },
    )
    assert chart_multi_sensor.status_code == 200
    chart_body = chart_multi_sensor.json()
    assert len(chart_body["series"]) == 2
    assert any(series["data"] for series in chart_body["series"])

    humidity_id = next(item.sensor_type_id for item in sensor_rows if item.code == "humidity")
    chart_multi_polygon = client.get(
        "/api/charts/multi-polygon",
        params={
            "sensor_type_id": humidity_id,
            "polygon_ids": "1,2,3",
            "aggregation": "raw",
        },
    )
    assert chart_multi_polygon.status_code == 200
    chart_polygon_body = chart_multi_polygon.json()
    assert len(chart_polygon_body["series"]) == 3
