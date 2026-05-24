# Eco Monitoring App

Веб-приложение для хранения и анализа экологических измерений.
Главная таблица данных: `measurements`.
Таблица `import_files` используется только для истории загрузок CSV.

## Текущий функционал

- Docker Compose: MySQL 8 + FastAPI backend
- Backend API:
  - загрузка CSV в `measurements`
  - история импортов
  - просмотр измерений с фильтрами и пагинацией
  - графики: multi-sensor и multi-polygon
  - чтение справочников
  - dashboard summary
- Frontend Angular:
  - Dashboard
  - реальная страница загрузки CSV
  - таблица измерений с фильтрами
  - графики на Apache ECharts
- Генератор тестовых CSV-файлов
- Backend тесты на `pytest`

## Структура

```text
eco-monitoring-app/
├── backend/
├── frontend/
├── docs/
├── sample_data/
├── docker-compose.yml
├── .env.example
├── README.md
└── PROJECT_REQUIREMENTS.md
```

## Подготовка окружения

```bash
cp .env.example .env
```

Для PowerShell:

```powershell
Copy-Item .env.example .env
```

## Запуск backend + MySQL

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed_data
```

Проверка:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)

## Генерация тестовых CSV

Скрипт создаёт по ~1000 строк для каждого полигона:

- `sample_data/polygon_1_measurements.csv`
- `sample_data/polygon_2_measurements.csv`
- `sample_data/polygon_3_measurements.csv`

Запуск:

```bash
python sample_data/generate_sample_csv.py
```

## Запуск frontend

```bash
cd frontend
npm install
npm start
```

Frontend: [http://localhost:4200](http://localhost:4200)

## Основные API endpoints

### Справочники

- `GET /api/polygons`
- `GET /api/sensor-types`
- `GET /api/measurement-units`

### Импорт CSV

- `POST /api/imports/csv`
- `GET /api/imports`

Поля формы `POST /api/imports/csv`:

- `file` (CSV)
- `polygon_id`
- `collector_last_name` (обязательно)
- `collector_first_name` (опционально)
- `collector_middle_name` (опционально)

Поддерживаемые колонки датчиков (RU/EN):

- `CO2` / `co2`
- `Влажность` / `humidity`
- `Температура` / `temperature`
- `Давление` / `pressure`
- `Освещённость` / `light`
- `Уровень шума` / `noise`

Важно по валидации импорта:

- обязательна колонка `Дата`
- пустые значения пропускаются
- некорректные числовые значения пропускаются
- количество пропусков возвращается в `skipped_values`
- статус импорта:
  - `processed` при успехе
  - `failed` при ошибке

### Измерения

- `GET /api/measurements`

Фильтры:

- `polygon_id`
- `sensor_type_id`
- `date_from`
- `date_to`
- `collector_id`
- `import_file_id`
- `limit`
- `offset`
- `sort_order=asc|desc` (по `measured_at`, по умолчанию `desc`)

### Графики

- `GET /api/charts/multi-sensor`
- `GET /api/charts/multi-polygon`

Дополнительно:

- `period=last_24h|last_7d|last_month`
- `aggregation=raw|hourly|daily`

### Dashboard

- `GET /api/dashboard/summary`

## Тесты backend

```bash
docker compose exec backend pytest -q
```

Покрыто:

- health endpoint
- чтение справочников
- импорт CSV
- появление записей в `measurements`
- обработка пропусков
- `GET /api/measurements`
- chart endpoints

## Полезные команды

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volume БД:

```bash
docker compose down -v
```

