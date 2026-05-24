# API

Префикс всех endpoint: `/api`

## Health

### `GET /api/health`

Проверка доступности backend.

Пример ответа:

```json
{ "status": "ok" }
```

## Справочники

### `GET /api/polygons`
### `GET /api/sensor-types`
### `GET /api/measurement-units`

Read-only API для frontend select-ов и страницы справочников.

## Импорт CSV

### `POST /api/imports/csv`

`multipart/form-data`:
- `file` (обязательно, `.csv`)
- `polygon_id` (обязательно)
- `collector_last_name` (обязательно)
- `collector_first_name` (опционально)
- `collector_middle_name` (опционально)

Пример ответа:

```json
{
  "import_file_id": 1,
  "file_name": "polygon_1_measurements.csv",
  "status": "processed",
  "rows_count": 1000,
  "measurements_count": 5914,
  "skipped_values": 86
}
```

### `GET /api/imports`

Фильтры:
- `polygon_id`
- `collector_id`
- `status`
- `date_from`
- `date_to`

## Измерения

### `GET /api/measurements`

Возвращает табличный список с join-данными:
- `measurement_id`
- `measured_at`
- `polygon_name`
- `sensor_name`, `sensor_code`
- `value`, `unit_symbol`
- `file_name`, `collector_last_name`

Фильтры:
- `polygon_id`
- `sensor_type_id`
- `date_from`, `date_to`
- `collector_id`
- `import_file_id`
- `limit`, `offset`
- `sort_order=asc|desc`

## Графики

### `GET /api/charts/multi-sensor`

Сценарий: несколько датчиков на одном полигоне.

Параметры:
- `polygon_id`
- `sensor_type_ids` (через запятую)
- `date_from`, `date_to` или `period`
- `aggregation=raw|hourly|daily`

### `GET /api/charts/multi-polygon`

Сценарий: один датчик на нескольких полигонах.

Параметры:
- `sensor_type_id`
- `polygon_ids` (через запятую)
- `date_from`, `date_to` или `period`
- `aggregation=raw|hourly|daily`

## Dashboard

### `GET /api/dashboard/summary`

Возвращает:
- количество полигонов;
- количество типов датчиков;
- количество измерений;
- количество CSV загрузок;
- последние 5 импортов.

## Пример cURL импорта

```bash
curl -X POST "http://localhost:8000/api/imports/csv" \
  -F "file=@sample_data/polygon_1_measurements.csv" \
  -F "polygon_id=1" \
  -F "collector_last_name=Petrov"
```
