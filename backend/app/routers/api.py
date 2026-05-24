from fastapi import APIRouter

from app.routers import charts, dashboard, health, imports, measurements, references

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(references.router)
api_router.include_router(imports.router)
api_router.include_router(measurements.router)
api_router.include_router(charts.router)
api_router.include_router(dashboard.router)
