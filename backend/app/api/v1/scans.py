"""POST /api/v1/scans — ingest a scan (unauthenticated, camera webhook)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scan import ScanIngest, ScanIngestResult
from app.services.scan_service import ingest_scan

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", response_model=ScanIngestResult, status_code=201)
async def create_scan(body: ScanIngest, db: Session = Depends(get_db)):
    try:
        result = await ingest_scan(
            db=db,
            camera_id_code=body.camera_id,
            plate=body.plate,
            vin=body.vin,
            latitude=body.latitude,
            longitude=body.longitude,
            scanned_at=body.scanned_at,
            image_url=body.image_url,
        )
        return ScanIngestResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
