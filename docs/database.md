# Database Design

## Таблицы

1. `polygons`  
   Справочник полигонов мониторинга.

2. `data_collectors`  
   Люди, которые загружают CSV.

3. `measurement_units`  
   Справочник единиц измерения (`°C`, `%`, `hPa`, `ppm`, `lx`, `dB`).

4. `sensor_types`  
   Справочник типов датчиков (`temperature`, `humidity`, `pressure`, `co2`, `light`, `noise`), связан с `measurement_units`.

5. `import_files`  
   История загрузок CSV: кто загрузил, для какого полигона, статус, число строк и измерений.

6. `measurements`  
   Главная факт-таблица измерений.

## Связи

- `polygons 1:N measurements`
- `sensor_types 1:N measurements`
- `measurement_units 1:N sensor_types`
- `measurement_units 1:N measurements`
- `import_files 1:N measurements`
- `polygons 1:N import_files`
- `data_collectors 1:N import_files`

## Почему это 3НФ

- Справочники вынесены в отдельные таблицы (`polygons`, `sensor_types`, `measurement_units`).
- В `measurements` хранятся только ключи и фактические значения (дата/время, value).
- Нет повторяющихся групп колонок вида `sensor_1`, `sensor_2`, ...
- Никакие неключевые поля не зависят транзитивно от других неключевых полей в одной таблице.

## Почему `measurements` — главная таблица

- Все аналитические запросы (таблица, фильтры, графики) читают данные именно из `measurements`.
- Каждая строка — одно измерение одного датчика в один момент времени на одном полигоне.
- `import_files` используется только как журнал импорта, а не как хранилище самих измерений.

## Почему нет `experiments`, `sensors`, `polygon_sensors`, `import_sensor_columns`

Для текущих требований эти сущности избыточны:
- усложняют модель и демо;
- не дают дополнительной пользы для сценария CSV → measurements → аналитика;
- нарушают принцип «минимально необходимой схемы» для курсовой.

## Индексы

В проекте используются индексы:
- `idx_measurements_polygon_sensor_time (polygon_id, sensor_type_id, measured_at)`
- `idx_measurements_sensor_time_polygon (sensor_type_id, measured_at, polygon_id)`
- `idx_measurements_time (measured_at)`
- `idx_measurements_import_file (import_file_id)`
- `idx_import_files_polygon_uploaded (polygon_id, uploaded_at)`
