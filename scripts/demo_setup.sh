#!/usr/bin/env bash
set -euo pipefail

echo "== Eco Monitoring demo setup =="

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed_data
docker run --rm -v "$(pwd):/workspace" -w /workspace python:3.12-slim python sample_data/generate_sample_csv.py

cat <<'MSG'

Setup completed.
Next steps:
1) Import sample CSV:
   curl -X POST "http://localhost:8000/api/imports/csv" \
     -F "file=@sample_data/polygon_1_measurements.csv" \
     -F "polygon_id=1" \
     -F "collector_last_name=Petrov"

2) Start frontend:
   cd frontend
   npm install
   npm start
MSG
