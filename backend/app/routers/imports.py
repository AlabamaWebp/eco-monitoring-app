from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImportFile
from app.schemas.imports import ImportCsvResponse, ImportListItem
from app.services.csv_import import import_measurements_from_csv

router = APIRouter(tags=["imports"])


@router.post("/imports/csv", response_model=ImportCsvResponse)
async def import_csv(
    file: UploadFile = File(...),
    polygon_id: int = Form(...),
    collector_last_name: str = Form(...),
    collector_first_name: str | None = Form(None),
    collector_middle_name: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ImportCsvResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Не указано имя файла.")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Поддерживаются только CSV-файлы.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Пустой файл.")

    try:
        result = import_measurements_from_csv(
            db,
            file_name=file.filename,
            file_content=content,
            polygon_id=polygon_id,
            collector_last_name=collector_last_name,
            collector_first_name=collector_first_name,
            collector_middle_name=collector_middle_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта CSV: {exc}") from exc

    return ImportCsvResponse(
        import_file_id=result.import_file_id,
        file_name=result.file_name,
        status=result.status,
        rows_count=result.rows_count,
        measurements_count=result.measurements_count,
        skipped_values=result.skipped_values,
    )


@router.get("/imports", response_model=list[ImportListItem])
def list_imports(
    polygon_id: int | None = Query(None),
    collector_id: int | None = Query(None),
    status: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> list[ImportListItem]:
    stmt = select(ImportFile).order_by(ImportFile.uploaded_at.desc())
    filters = []

    if polygon_id is not None:
        filters.append(ImportFile.polygon_id == polygon_id)
    if collector_id is not None:
        filters.append(ImportFile.collector_id == collector_id)
    if status:
        filters.append(ImportFile.status == status)
    if date_from is not None:
        filters.append(ImportFile.uploaded_at >= date_from)
    if date_to is not None:
        filters.append(ImportFile.uploaded_at <= date_to)

    if filters:
        stmt = stmt.where(and_(*filters))

    imports = db.scalars(stmt).all()
    return [
        ImportListItem(
            import_file_id=item.import_file_id,
            file_name=item.file_name,
            polygon_name=item.polygon.name,
            collector_last_name=item.collector.last_name,
            uploaded_at=item.uploaded_at,
            rows_count=item.rows_count,
            measurements_count=item.measurements_count,
            status=item.status,
            error_message=item.error_message,
        )
        for item in imports
    ]

