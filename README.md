# Eco Monitoring App

Веб-приложение для хранения и анализа экологических измерений с полигонов.

Ключевая идея проекта: CSV импортируется в **нормализованный длинный формат**, где каждая ячейка датчика становится отдельной строкой в таблице `measurements`.

## Технологии

- Backend: Python, FastAPI, SQLAlchemy, Alembic
- Database: MySQL 8 (Docker Compose)
- Frontend: Angular, TypeScript, SCSS
- Графики: Apache ECharts

## Быстрый демонстрационный запуск

### Вариант 1: вручную

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed_data
docker run --rm -v <project_path>:/workspace -w //workspace python:3.12-slim python sample_data/generate_sample_csv.py
```

Пример для PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed_data
docker run --rm -v "${PWD}:/workspace" -w /workspace python:3.12-slim python sample_data/generate_sample_csv.py
```

Импорт sample CSV:

```bash
curl -X POST "http://localhost:8000/api/imports/csv" \
  -F "file=@sample_data/polygon_1_measurements.csv" \
  -F "polygon_id=1" \
  -F "collector_last_name=Petrov"
```

Запуск frontend:

```bash
cd frontend
npm install
npm start
```

Открыть:
- Backend Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:4200](http://localhost:4200)

### Вариант 2: через demo-скрипты

- Windows: `./scripts/demo_setup.ps1`
- Linux/macOS: `bash ./scripts/demo_setup.sh`

## Структура проекта

```text
eco-monitoring-app/
├── backend/
├── frontend/
├── docs/
├── sample_data/
├── scripts/
├── docker-compose.yml
├── .env.example
├── README.md
└── PROJECT_REQUIREMENTS.md
```

## Как устроен CSV-импорт

1. Пользователь выбирает полигон и указывает фамилию.
2. Загружает CSV с колонкой `Дата` и колонками датчиков.
3. Backend создаёт запись в `import_files`.
4. Каждая непустая корректная ячейка датчика записывается в `measurements`.
5. Пустые или некорректные числовые значения пропускаются и считаются в `skipped_values`.

Поддерживаемые колонки датчиков (RU/EN):
- `CO2` / `co2`
- `Влажность` / `humidity`
- `Температура` / `temperature`
- `Давление` / `pressure`
- `Освещённость` / `light`
- `Уровень шума` / `noise`

## Таблицы БД

- `polygons`
- `data_collectors`
- `measurement_units`
- `sensor_types`
- `import_files` (история загрузок)
- `measurements` (**главная таблица проекта**)

Почему `measurements` главная:
- все фильтры, таблицы и графики строятся по ней;
- это факт-таблица временных рядов;
- `import_files` хранит только аудит импорта.

## Основные страницы frontend

- Dashboard
- Загрузка CSV
- Измерения (таблица + фильтры + пагинация)
- Графики (2 режима)
- Справочники (read-only)

## API endpoints

### Справочники
- `GET /api/polygons`
- `GET /api/sensor-types`
- `GET /api/measurement-units`

### Импорты
- `POST /api/imports/csv`
- `GET /api/imports`

### Измерения
- `GET /api/measurements`

### Графики
- `GET /api/charts/multi-sensor`
- `GET /api/charts/multi-polygon`

### Dashboard
- `GET /api/dashboard/summary`

## Тесты и проверки

Backend tests:

```bash
docker compose exec backend pytest -q
```

Frontend build:

```bash
cd frontend
npx ng build
```

Рекомендуемый полный чек:

```bash
docker compose config
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed_data
docker compose exec backend pytest -q
cd frontend && npx ng build
```

## Типичные проблемы

1. `npm` в PowerShell не запускается из-за policy  
   Используйте `npm.cmd install` / `npx.cmd ng build`.

2. Пустые графики  
   Sample CSV начинается с `2025-01-01`. На странице графиков используйте кнопку **"Период sample-данных"**.

3. Ошибка импорта CSV  
   Проверьте:
   - наличие колонки `Дата`;
   - известные названия датчиков;
   - расширение файла `.csv`.
