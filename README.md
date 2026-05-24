# Eco Monitoring App

Стартовый каркас курсового проекта по БД для хранения и анализа экологических измерений.

Текущий этап: подготовлена стабильная база проекта (backend + MySQL + миграции + seed + frontend-заглушки).

## 1. Структура

```text
eco-monitoring-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docs/
├── sample_data/
├── docker-compose.yml
├── .env.example
├── README.md
└── PROJECT_REQUIREMENTS.md
```

## 2. Технологии

- Backend: Python, FastAPI, SQLAlchemy, Alembic
- Database: MySQL 8 (Docker Compose)
- Frontend: Angular, TypeScript, SCSS
- Charts (следующий этап): Apache ECharts

## 3. Быстрый старт

### 3.1 Подготовка `.env`

Скопируйте файл:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 3.2 Запуск MySQL и Backend в Docker

```bash
docker compose up -d --build
```

Проверка:

```bash
docker compose ps
docker compose logs -f backend
```

Backend:
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3.3 Применение миграций

```bash
docker compose exec backend alembic upgrade head
```

### 3.4 Наполнение базовых справочников (seed)

```bash
docker compose exec backend python -m app.seed_data
```

Будут добавлены:
- единицы измерения: `°C`, `%`, `hPa`, `ppm`, `lx`, `dB`
- типы датчиков: `temperature`, `humidity`, `pressure`, `co2`, `light`, `noise`
- тестовые полигоны: `Polygon #1`, `Polygon #2`, `Polygon #3`

## 4. Локальный запуск frontend

```bash
cd frontend
npm install
npm start
```

Frontend: [http://localhost:4200](http://localhost:4200)

Реализованы страницы-заглушки:
- Dashboard
- Загрузка CSV
- Измерения
- Графики

## 5. Что уже реализовано

### Backend
- Базовая модульная структура (`models`, `schemas`, `routers`, `services`, `core`)
- Подключение к MySQL через SQLAlchemy
- CORS для `http://localhost:4200`
- Endpoint `GET /api/health`
- Модели:
  - `polygons`
  - `data_collectors`
  - `measurement_units`
  - `sensor_types`
  - `import_files`
  - `measurements`

### Alembic
- Настроен `alembic/env.py`
- Добавлена стартовая миграция со всеми таблицами, внешними ключами и индексами
- Индексы `measurements`:
  - `(polygon_id, sensor_type_id, measured_at)`
  - `(sensor_type_id, measured_at, polygon_id)`
  - `(measured_at)`
  - `(import_file_id)`

### Frontend
- Angular проект с роутингом
- Layout с навигацией
- Светлая аккуратная тема
- Основной цвет интерфейса синий/фиолетовый (не зелёный)

## 6. Полезные команды

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volume БД:

```bash
docker compose down -v
```

Создать новую миграцию:

```bash
docker compose exec backend alembic revision --autogenerate -m "message"
```

