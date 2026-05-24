Write-Host "== Eco Monitoring demo setup =="

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example"
}

docker compose up -d --build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker compose exec backend alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker compose exec backend python -m app.seed_data
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker run --rm -v "${PWD}:/workspace" -w /workspace python:3.12-slim python sample_data/generate_sample_csv.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Setup completed."
Write-Host "Next steps:"
Write-Host "1) Import sample CSV:"
Write-Host '   curl -X POST "http://localhost:8000/api/imports/csv" -F "file=@sample_data/polygon_1_measurements.csv" -F "polygon_id=1" -F "collector_last_name=Petrov"'
Write-Host "2) Start frontend:"
Write-Host "   cd frontend"
Write-Host "   npm install"
Write-Host "   npm start"
