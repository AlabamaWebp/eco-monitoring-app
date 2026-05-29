from sqlalchemy import func, select

from app.models import ImportFile, Measurement, MeasurementUnit, Polygon, SensorType


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


def test_polygon_crud(client, seeded_db):
    create_response = client.post(
        "/api/polygons",
        json={"name": "Test Polygon", "location": "Zone A", "description": "Demo polygon"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    polygon_id = created["polygon_id"]

    update_response = client.put(
        f"/api/polygons/{polygon_id}",
        json={"name": "Updated Polygon", "location": "Zone B", "description": "Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Polygon"

    delete_response = client.delete(f"/api/polygons/{polygon_id}")
    assert delete_response.status_code == 204
    assert seeded_db.get(Polygon, polygon_id) is None


def test_polygon_delete_blocked_by_measurements(client, seeded_db):
    polygon = client.post("/api/polygons", json={"name": "Polygon In Use", "location": "", "description": ""}).json()
    sensor_type = seeded_db.scalar(select(SensorType).where(SensorType.code == "temperature"))
    assert sensor_type is not None

    create_measurement = client.post(
        "/api/measurements",
        json={
            "polygon_id": polygon["polygon_id"],
            "sensor_type_id": sensor_type.sensor_type_id,
            "measured_at": "2025-01-05T12:00:00",
            "value": 64.5,
        },
    )
    assert create_measurement.status_code == 201

    delete_response = client.delete(f"/api/polygons/{polygon['polygon_id']}")
    assert delete_response.status_code == 409
    assert "измер" in delete_response.json()["detail"].lower()


def test_polygon_delete_blocked_by_imports(client, seeded_db):
    polygon = client.post("/api/polygons", json={"name": "Polygon With Import", "location": "", "description": ""}).json()
    bad_csv = ("CO2,Humidity\n420,61\n").encode("utf-8")
    import_response = _import_csv(client, bad_csv, polygon_id=polygon["polygon_id"], last_name="Petrov")
    assert import_response.status_code == 400

    delete_response = client.delete(f"/api/polygons/{polygon['polygon_id']}")
    assert delete_response.status_code == 409
    assert "загруз" in delete_response.json()["detail"].lower()


def test_sensor_type_crud_and_unique_code(client, seeded_db):
    unit = seeded_db.scalar(select(MeasurementUnit).where(MeasurementUnit.symbol == "ppm"))
    assert unit is not None

    create_response = client.post(
        "/api/sensor-types",
        json={"name": "VOC", "code": "voc", "unit_id": unit.unit_id, "description": "Volatile compounds"},
    )
    assert create_response.status_code == 201
    sensor_type_id = create_response.json()["sensor_type_id"]

    update_response = client.put(
        f"/api/sensor-types/{sensor_type_id}",
        json={"name": "VOC Updated", "code": "voc_updated", "unit_id": unit.unit_id, "description": ""},
    )
    assert update_response.status_code == 200
    assert update_response.json()["code"] == "voc_updated"

    duplicate_response = client.post(
        "/api/sensor-types",
        json={"name": "Duplicate", "code": "temperature", "unit_id": unit.unit_id, "description": ""},
    )
    assert duplicate_response.status_code == 409

    delete_response = client.delete(f"/api/sensor-types/{sensor_type_id}")
    assert delete_response.status_code == 204


def test_sensor_type_delete_blocked_by_measurements(client, seeded_db):
    unit = seeded_db.scalar(select(MeasurementUnit).where(MeasurementUnit.symbol == "ppm"))
    assert unit is not None
    sensor_response = client.post(
        "/api/sensor-types",
        json={"name": "PM2.5", "code": "pm25", "unit_id": unit.unit_id, "description": ""},
    )
    assert sensor_response.status_code == 201
    sensor_type_id = sensor_response.json()["sensor_type_id"]

    create_measurement = client.post(
        "/api/measurements",
        json={
            "polygon_id": 1,
            "sensor_type_id": sensor_type_id,
            "measured_at": "2025-01-05T12:00:00",
            "value": 12.4,
        },
    )
    assert create_measurement.status_code == 201

    delete_response = client.delete(f"/api/sensor-types/{sensor_type_id}")
    assert delete_response.status_code == 409
    assert "измер" in delete_response.json()["detail"].lower()


def test_measurement_units_crud_and_delete_restrictions(client, seeded_db):
    create_response = client.post(
        "/api/measurement-units",
        json={"name": "Milligram per cubic meter", "symbol": "mg/m3", "description": "Concentration"},
    )
    assert create_response.status_code == 201
    unit_id = create_response.json()["unit_id"]

    update_response = client.put(
        f"/api/measurement-units/{unit_id}",
        json={"name": "Milligram/m3", "symbol": "mg_m3", "description": ""},
    )
    assert update_response.status_code == 200
    assert update_response.json()["symbol"] == "mg_m3"

    create_sensor_response = client.post(
        "/api/sensor-types",
        json={"name": "Dust", "code": "dust", "unit_id": unit_id, "description": ""},
    )
    assert create_sensor_response.status_code == 201
    sensor_type_id = create_sensor_response.json()["sensor_type_id"]

    blocked_by_sensor_type = client.delete(f"/api/measurement-units/{unit_id}")
    assert blocked_by_sensor_type.status_code == 409

    new_unit = client.post(
        "/api/measurement-units",
        json={"name": "Percent by volume", "symbol": "vol%", "description": ""},
    )
    assert new_unit.status_code == 201
    replacement_unit_id = new_unit.json()["unit_id"]

    update_sensor = client.put(
        f"/api/sensor-types/{sensor_type_id}",
        json={"name": "Dust", "code": "dust", "unit_id": replacement_unit_id, "description": ""},
    )
    assert update_sensor.status_code == 200

    measurement_create = client.post(
        "/api/measurements",
        json={
            "polygon_id": 1,
            "sensor_type_id": sensor_type_id,
            "measured_at": "2025-01-06T08:00:00",
            "value": 5.1,
        },
    )
    assert measurement_create.status_code == 201
    measurement_id = measurement_create.json()["measurement_id"]

    measurement = seeded_db.get(Measurement, measurement_id)
    assert measurement is not None
    measurement.unit_id = unit_id
    seeded_db.commit()

    delete_unit_with_measurements = client.delete(f"/api/measurement-units/{unit_id}")
    assert delete_unit_with_measurements.status_code == 409

    free_unit_create = client.post(
        "/api/measurement-units",
        json={"name": "Free Unit", "symbol": "free_u", "description": ""},
    )
    free_unit_id = free_unit_create.json()["unit_id"]
    free_delete = client.delete(f"/api/measurement-units/{free_unit_id}")
    assert free_delete.status_code == 204


def test_measurements_manual_create_update_delete_and_get(client, seeded_db):
    sensor_temperature = seeded_db.scalar(select(SensorType).where(SensorType.code == "temperature"))
    sensor_humidity = seeded_db.scalar(select(SensorType).where(SensorType.code == "humidity"))
    assert sensor_temperature is not None
    assert sensor_humidity is not None

    create_response = client.post(
        "/api/measurements",
        json={
            "polygon_id": 1,
            "sensor_type_id": sensor_temperature.sensor_type_id,
            "measured_at": "2025-01-05T12:00:00",
            "value": 23.4,
        },
    )
    assert create_response.status_code == 201
    measurement_id = create_response.json()["measurement_id"]

    created_measurement = seeded_db.get(Measurement, measurement_id)
    assert created_measurement is not None
    assert created_measurement.import_file_id is None
    assert created_measurement.unit_id == sensor_temperature.unit_id

    update_response = client.put(
        f"/api/measurements/{measurement_id}",
        json={
            "polygon_id": 2,
            "sensor_type_id": sensor_humidity.sensor_type_id,
            "measured_at": "2025-01-05T13:00:00",
            "value": 55.1,
        },
    )
    assert update_response.status_code == 200
    updated_measurement = seeded_db.get(Measurement, measurement_id)
    assert updated_measurement is not None
    assert updated_measurement.polygon_id == 2
    assert updated_measurement.sensor_type_id == sensor_humidity.sensor_type_id
    assert updated_measurement.unit_id == sensor_humidity.unit_id
    assert updated_measurement.import_file_id is None

    list_response = client.get("/api/measurements", params={"polygon_id": 2})
    assert list_response.status_code == 200
    rows = list_response.json()["items"]
    listed = next((item for item in rows if item["measurement_id"] == measurement_id), None)
    assert listed is not None
    assert listed["import_file_id"] is None
    assert listed["file_name"] is None
    assert listed["collector_last_name"] is None

    delete_response = client.delete(f"/api/measurements/{measurement_id}")
    assert delete_response.status_code == 204
    assert seeded_db.get(Measurement, measurement_id) is None


def test_measurements_update_imported_keeps_import_file_id(client, seeded_db):
    csv_data = (
        "Дата,CO2,Влажность\n"
        "2025-01-01 00:00:00,420,61\n"
    ).encode("utf-8")
    imported = _import_csv(client, csv_data)
    assert imported.status_code == 200
    import_file_id = imported.json()["import_file_id"]

    measurement = seeded_db.scalar(
        select(Measurement).where(Measurement.import_file_id == import_file_id).order_by(Measurement.measurement_id.asc())
    )
    assert measurement is not None
    original_import_file_id = measurement.import_file_id

    sensor_humidity = seeded_db.scalar(select(SensorType).where(SensorType.code == "humidity"))
    assert sensor_humidity is not None

    update_response = client.put(
        f"/api/measurements/{measurement.measurement_id}",
        json={
            "polygon_id": measurement.polygon_id,
            "sensor_type_id": sensor_humidity.sensor_type_id,
            "measured_at": "2025-01-01T02:00:00",
            "value": 66.0,
        },
    )
    assert update_response.status_code == 200

    updated = seeded_db.get(Measurement, measurement.measurement_id)
    assert updated is not None
    assert updated.import_file_id == original_import_file_id
