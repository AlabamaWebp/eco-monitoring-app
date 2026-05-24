# PROJECT_REQUIREMENTS.md

# Eco Monitoring App — требования к курсовому проекту

## 1. Назначение проекта

Проект представляет собой веб-приложение для хранения, просмотра, фильтрации и анализа экологических измерений, собранных на разных полигонах.

Система должна позволять загружать данные из CSV-файлов, сохранять их в нормализованной базе данных MySQL, просматривать загруженные измерения, фильтровать их по разным критериям и строить графики.

Проект выполняется как курсовая работа по базам данных. База данных должна быть нормализована не ниже третьей нормальной формы.

---

## 2. Предметная область

На множестве экологических полигонов собираются данные с разных датчиков.

Примеры датчиков:

- CO2;
- влажность;
- температура;
- атмосферное давление;
- освещённость;
- уровень шума;
- загрязнение воздуха;
- загрязнение воды.

На разных полигонах могут присутствовать разные наборы датчиков. Например, на одном полигоне могут быть данные по CO2, влажности и температуре, а на другом — только по влажности и давлению.

Человек проходит по полигонам, собирает данные и загружает CSV-файл в приложение. При загрузке он указывает:

- полигон;
- свою фамилию;
- CSV-файл с измерениями.

CSV-файл имеет широкий формат:

```csv
Дата,CO2,Влажность,Температура,Давление
2025-01-01 12:00,420,61,22.4,745
2025-01-01 13:00,430,63,22.8,746
```

В базе данные должны храниться в длинном формате:

```text
Дата и время | Полигон | Тип датчика | Значение | Единица измерения | Файл импорта
```

Одна ячейка значения датчика из CSV должна превращаться в одну строку таблицы `measurements`.

---

## 3. Главная идея структуры БД

Главная таблица базы данных — `measurements`.

Таблица `import_files` является второстепенной. Она нужна только для хранения информации о факте загрузки CSV-файла: имя файла, дата загрузки, кто загрузил, для какого полигона и сколько записей было импортировано.

Все основные просмотры, фильтры и графики должны строиться через таблицу `measurements`.

---

## 4. Технологический стек

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PyMySQL или mysqlclient
- Pydantic
- pandas или стандартный csv-модуль для импорта CSV

### Database

- MySQL 8
- Запуск через Docker Compose

### Frontend

- Angular
- TypeScript
- SCSS
- Angular Reactive Forms
- Angular Router
- HTTP Client

### Charts

Рекомендуется использовать:

- Apache ECharts

Причина: ECharts хорошо подходит для аналитических графиков, временных рядов, нескольких линий, легенд, tooltip и масштабирования по времени.

### UI

Интерфейс должен быть современным, аккуратным и светлым.

Основной цвет не должен быть зелёным.

Рекомендуемая палитра:

```text
Primary: #2563EB
Accent: #7C3AED
Background: #F8FAFC
Surface/Card: #FFFFFF
Text: #0F172A
Muted text: #64748B
Border: #E2E8F0
Error: #DC2626
Warning: #F59E0B
Success: #16A34A
```

Зелёный можно использовать только как вспомогательный цвет для статусов, но не как основной цвет интерфейса.

---

## 5. Структура репозитория

Проект должен быть монорепозиторием:

```text
eco-monitoring-app/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── core/
│   │
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── angular.json
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   ├── database.md
│   ├── api.md
│   ├── csv-format.md
│   └── course-report-notes.md
│
├── sample_data/
│   └── sample_measurements.csv
│
├── docker-compose.yml
├── .env.example
├── README.md
└── PROJECT_REQUIREMENTS.md
```

---

## 6. Модель базы данных

База данных должна содержать следующие таблицы:

1. `polygons`
2. `data_collectors`
3. `measurement_units`
4. `sensor_types`
5. `import_files`
6. `measurements`

---

## 7. Таблица `polygons`

Назначение: хранение информации об экологических полигонах.

Поля:

```sql
polygon_id BIGINT PRIMARY KEY AUTO_INCREMENT
name VARCHAR(255) NOT NULL
location VARCHAR(255) NULL
description TEXT NULL
created_at DATETIME NOT NULL
updated_at DATETIME NULL
```

Требования:

- название полигона обязательно;
- один полигон может иметь много измерений;
- один полигон может иметь много загруженных CSV-файлов.

---

## 8. Таблица `data_collectors`

Назначение: хранение информации о людях, которые загружают CSV-файлы.

Поля:

```sql
collector_id BIGINT PRIMARY KEY AUTO_INCREMENT
last_name VARCHAR(255) NOT NULL
first_name VARCHAR(255) NULL
middle_name VARCHAR(255) NULL
created_at DATETIME NOT NULL
```

Требования:

- при загрузке CSV пользователь обязательно указывает фамилию;
- если человека с такой фамилией ещё нет, приложение может создать новую запись;
- в будущем можно будет расширить таблицу до полноценного справочника сотрудников.

---

## 9. Таблица `measurement_units`

Назначение: справочник единиц измерения.

Поля:

```sql
unit_id BIGINT PRIMARY KEY AUTO_INCREMENT
name VARCHAR(255) NOT NULL
symbol VARCHAR(50) NOT NULL
description TEXT NULL
```

Примеры данных:

```text
Градус Цельсия | °C
Процент | %
Миллиметр ртутного столба | mmHg
Гектопаскаль | hPa
Частей на миллион | ppm
Люкс | lx
Децибел | dB
```

---

## 10. Таблица `sensor_types`

Назначение: справочник типов датчиков или измеряемых показателей.

Поля:

```sql
sensor_type_id BIGINT PRIMARY KEY AUTO_INCREMENT
unit_id BIGINT NOT NULL
name VARCHAR(255) NOT NULL
code VARCHAR(100) NOT NULL UNIQUE
description TEXT NULL

FOREIGN KEY (unit_id) REFERENCES measurement_units(unit_id)
```

Примеры данных:

```text
CO2 | co2 | ppm
Влажность | humidity | %
Температура | temperature | °C
Давление | pressure | hPa
Освещённость | light | lx
Уровень шума | noise | dB
```

Важно:

- поля `normal_min` и `normal_max` не нужны;
- нормативные значения в текущей версии проекта не реализуются;
- единица измерения хранится через внешний ключ `unit_id`.

---

## 11. Таблица `import_files`

Назначение: хранение информации о загруженных CSV-файлах.

Эта таблица не является главной. Она нужна для истории загрузок и аудита.

Поля:

```sql
import_file_id BIGINT PRIMARY KEY AUTO_INCREMENT
polygon_id BIGINT NOT NULL
collector_id BIGINT NOT NULL
file_name VARCHAR(255) NOT NULL
uploaded_at DATETIME NOT NULL
rows_count INT NOT NULL DEFAULT 0
measurements_count INT NOT NULL DEFAULT 0
status VARCHAR(50) NOT NULL
error_message TEXT NULL

FOREIGN KEY (polygon_id) REFERENCES polygons(polygon_id)
FOREIGN KEY (collector_id) REFERENCES data_collectors(collector_id)
```

Примеры `status`:

```text
uploaded
processed
failed
```

---

## 12. Таблица `measurements`

Назначение: главная таблица всех экологических измерений.

Поля:

```sql
measurement_id BIGINT PRIMARY KEY AUTO_INCREMENT
polygon_id BIGINT NOT NULL
sensor_type_id BIGINT NOT NULL
unit_id BIGINT NOT NULL
import_file_id BIGINT NULL
measured_at DATETIME NOT NULL
value DECIMAL(16,4) NOT NULL
created_at DATETIME NOT NULL

FOREIGN KEY (polygon_id) REFERENCES polygons(polygon_id)
FOREIGN KEY (sensor_type_id) REFERENCES sensor_types(sensor_type_id)
FOREIGN KEY (unit_id) REFERENCES measurement_units(unit_id)
FOREIGN KEY (import_file_id) REFERENCES import_files(import_file_id)
```

Важно:

- `measurements` — центральная таблица проекта;
- одна строка — одно значение одного датчика в один момент времени на одном полигоне;
- `import_file_id` может быть `NULL`, если данные были внесены вручную;
- `unit_id` дублирует единицу из `sensor_types` намеренно, чтобы удобнее строить отчёты и сохранять историческую единицу измерения на момент импорта;
- названия датчиков не хранятся напрямую в `measurements`, только ссылки на справочники.

---

## 13. Индексы

Для удобной фильтрации и построения графиков нужно создать индексы:

```sql
CREATE INDEX idx_measurements_polygon_sensor_time
ON measurements (polygon_id, sensor_type_id, measured_at);

CREATE INDEX idx_measurements_sensor_time_polygon
ON measurements (sensor_type_id, measured_at, polygon_id);

CREATE INDEX idx_measurements_time
ON measurements (measured_at);

CREATE INDEX idx_measurements_import_file
ON measurements (import_file_id);

CREATE INDEX idx_import_files_polygon_uploaded
ON import_files (polygon_id, uploaded_at);
```

Эти индексы нужны для сценариев:

- построить график нескольких датчиков на одном полигоне;
- сравнить один датчик на нескольких полигонах;
- отфильтровать данные по периоду;
- открыть все данные из конкретного CSV-файла.

---

## 14. Основные связи

```text
polygons 1:N measurements
sensor_types 1:N measurements
measurement_units 1:N sensor_types
measurement_units 1:N measurements
import_files 1:N measurements
polygons 1:N import_files
data_collectors 1:N import_files
```

---

## 15. Нормализация

База данных должна соответствовать 3НФ.

Обоснование:

1. Все таблицы имеют первичные ключи.
2. Все неключевые атрибуты зависят от первичного ключа своей таблицы.
3. Справочные данные вынесены в отдельные таблицы.
4. Названия полигонов, датчиков и единиц измерения не дублируются в таблице измерений.
5. Нет повторяющихся групп колонок вида `sensor1`, `sensor2`, `sensor3` в базе данных.
6. CSV имеет широкий формат, но при импорте преобразуется в нормализованный длинный формат.

---

## 16. Импорт CSV

### Формат CSV

Обязательная колонка:

```text
Дата
```

Остальные колонки — названия датчиков:

```csv
Дата,CO2,Влажность,Температура,Давление
2025-01-01 12:00,420,61,22.4,745
2025-01-01 13:00,430,63,22.8,746
```

### Алгоритм импорта

1. Пользователь выбирает полигон.
2. Пользователь указывает фамилию.
3. Пользователь выбирает CSV-файл.
4. Backend сохраняет запись в `import_files`.
5. Backend читает CSV.
6. Backend находит колонку `Дата`.
7. Backend определяет остальные колонки как типы датчиков.
8. Для каждой колонки датчика backend ищет запись в `sensor_types`.
9. Если тип датчика отсутствует, backend должен вернуть понятную ошибку или предложить создать его в справочнике.
10. Для каждой строки CSV и каждой колонки датчика создаётся запись в `measurements`.
11. Backend обновляет `rows_count`, `measurements_count` и `status` в `import_files`.

### Обработка отсутствующих значений

Если в CSV значение пустое:

- запись в `measurements` не создаётся;
- импорт продолжается;
- желательно учитывать количество пропущенных значений в логике импорта или сообщении пользователю.

---

## 17. API backend

Backend должен иметь префикс:

```text
/api
```

### Polygons

```text
GET    /api/polygons
GET    /api/polygons/{polygon_id}
POST   /api/polygons
PUT    /api/polygons/{polygon_id}
DELETE /api/polygons/{polygon_id}
```

### Sensor types

```text
GET    /api/sensor-types
GET    /api/sensor-types/{sensor_type_id}
POST   /api/sensor-types
PUT    /api/sensor-types/{sensor_type_id}
DELETE /api/sensor-types/{sensor_type_id}
```

### Measurement units

```text
GET    /api/measurement-units
POST   /api/measurement-units
PUT    /api/measurement-units/{unit_id}
DELETE /api/measurement-units/{unit_id}
```

### Data collectors

```text
GET    /api/data-collectors
POST   /api/data-collectors
```

### CSV imports

```text
POST   /api/imports/csv
GET    /api/imports
GET    /api/imports/{import_file_id}
```

### Measurements

```text
GET    /api/measurements
POST   /api/measurements
PUT    /api/measurements/{measurement_id}
DELETE /api/measurements/{measurement_id}
```

Фильтры для `GET /api/measurements`:

```text
polygon_id
sensor_type_id
date_from
date_to
collector_id
import_file_id
limit
offset
```

### Charts

График нескольких датчиков на одном полигоне:

```text
GET /api/charts/multi-sensor
```

Параметры:

```text
polygon_id
sensor_type_ids
date_from
date_to
```

Сравнение одного датчика на нескольких полигонах:

```text
GET /api/charts/multi-polygon
```

Параметры:

```text
sensor_type_id
polygon_ids
date_from
date_to
```

---

## 18. Основные страницы frontend

### 1. Dashboard

Главная страница.

Показывает:

- количество полигонов;
- количество типов датчиков;
- общее количество измерений;
- последние загрузки CSV;
- быстрые кнопки перехода к загрузке и графикам.

### 2. Загрузка CSV

Функции:

- выбор полигона;
- ввод фамилии загрузившего;
- выбор CSV-файла;
- предпросмотр названий колонок;
- загрузка файла;
- отображение результата импорта.

### 3. Просмотр измерений

Функции:

- таблица всех измерений;
- фильтр по полигону;
- фильтр по датчику;
- фильтр по периоду;
- фильтр по загрузившему;
- пагинация.

### 4. Графики

Функции:

- выбрать один полигон;
- выбрать несколько датчиков;
- выбрать период;
- построить график с несколькими линиями.

Пример:

```text
Полигон №1: CO2 + Влажность за март
```

### 5. Сравнение полигонов

Функции:

- выбрать один тип датчика;
- выбрать несколько полигонов;
- выбрать период;
- построить график сравнения.

Пример:

```text
Влажность на полигоне №1 и полигоне №2 за одинаковый период
```

### 6. Справочники

CRUD-страницы:

- полигоны;
- типы датчиков;
- единицы измерения.

---

## 19. Требования к интерфейсу

Интерфейс должен быть:

- современным;
- аккуратным;
- светлым;
- понятным для пользователя;
- без зелёного цвета как основного;
- похожим на аналитическую панель.

Желательные элементы:

- верхняя навигация или боковое меню;
- карточки статистики;
- таблицы с фильтрами;
- формы с валидацией;
- графики с легендой;
- уведомления об успешной загрузке или ошибке.

---

## 20. Примеры SQL-запросов для отчёта

### 1. Получить все измерения по конкретному полигону

```sql
SELECT
    m.measured_at,
    p.name AS polygon_name,
    st.name AS sensor_name,
    m.value,
    mu.symbol AS unit
FROM measurements m
JOIN polygons p ON p.polygon_id = m.polygon_id
JOIN sensor_types st ON st.sensor_type_id = m.sensor_type_id
JOIN measurement_units mu ON mu.unit_id = m.unit_id
WHERE m.polygon_id = 1
ORDER BY m.measured_at;
```

### 2. Построить график CO2 и влажности на одном полигоне

```sql
SELECT
    m.measured_at,
    st.code AS sensor_code,
    st.name AS sensor_name,
    m.value,
    mu.symbol AS unit
FROM measurements m
JOIN sensor_types st ON st.sensor_type_id = m.sensor_type_id
JOIN measurement_units mu ON mu.unit_id = m.unit_id
WHERE m.polygon_id = 1
  AND st.code IN ('co2', 'humidity')
  AND m.measured_at BETWEEN '2025-01-01 00:00:00' AND '2025-01-31 23:59:59'
ORDER BY m.measured_at, st.code;
```

### 3. Сравнить влажность на двух полигонах

```sql
SELECT
    m.measured_at,
    p.name AS polygon_name,
    m.value,
    mu.symbol AS unit
FROM measurements m
JOIN polygons p ON p.polygon_id = m.polygon_id
JOIN sensor_types st ON st.sensor_type_id = m.sensor_type_id
JOIN measurement_units mu ON mu.unit_id = m.unit_id
WHERE st.code = 'humidity'
  AND m.polygon_id IN (1, 2)
ORDER BY m.measured_at, p.name;
```

### 4. Получить все данные из конкретного CSV-файла

```sql
SELECT
    i.file_name,
    m.measured_at,
    p.name AS polygon_name,
    st.name AS sensor_name,
    m.value,
    mu.symbol AS unit
FROM measurements m
JOIN import_files i ON i.import_file_id = m.import_file_id
JOIN polygons p ON p.polygon_id = m.polygon_id
JOIN sensor_types st ON st.sensor_type_id = m.sensor_type_id
JOIN measurement_units mu ON mu.unit_id = m.unit_id
WHERE m.import_file_id = 1
ORDER BY m.measured_at;
```

### 5. Получить список последних загрузок

```sql
SELECT
    i.import_file_id,
    i.file_name,
    p.name AS polygon_name,
    dc.last_name AS collector_last_name,
    i.uploaded_at,
    i.rows_count,
    i.measurements_count,
    i.status
FROM import_files i
JOIN polygons p ON p.polygon_id = i.polygon_id
JOIN data_collectors dc ON dc.collector_id = i.collector_id
ORDER BY i.uploaded_at DESC;
```

---

## 21. Seed-данные

При первом запуске желательно автоматически создать базовые справочники.

### Единицы измерения

```text
°C
%
hPa
ppm
lx
dB
```

### Типы датчиков

```text
temperature
humidity
pressure
co2
light
noise
```

### Пример полигонов

```text
Полигон №1
Полигон №2
Полигон №3
```

---

## 22. Требования к качеству кода

Код должен быть:

- понятным;
- структурированным;
- не перегруженным;
- с комментариями в сложных местах;
- разделённым по слоям: models, schemas, routers, services;
- пригодным для демонстрации на защите курсовой работы.

Backend не должен содержать всю логику в `main.py`.

Frontend не должен содержать всю логику в одном компоненте.

---

## 23. Минимальный результат, который должен работать

К минимально рабочей версии относятся:

1. Запуск MySQL через Docker Compose.
2. Запуск FastAPI backend.
3. Подключение backend к MySQL.
4. Создание таблиц через Alembic.
5. CRUD для полигонов, типов датчиков и единиц измерения.
6. Загрузка CSV.
7. Сохранение измерений в таблицу `measurements`.
8. Просмотр измерений в Angular.
9. Фильтрация измерений.
10. Построение графика нескольких датчиков на одном полигоне.
11. Сравнение одного датчика на нескольких полигонах.

---

## 24. Что важно для защиты

В проекте нужно уметь показать:

1. ER-диаграмму базы данных.
2. Нормализацию до 3НФ.
3. Таблицы MySQL.
4. Загрузку CSV.
5. Просмотр данных.
6. Фильтрацию.
7. Построение графиков.
8. Примеры SQL-запросов.
9. Связь frontend, backend и database.
10. Обоснование того, почему `measurements` является главной таблицей.
