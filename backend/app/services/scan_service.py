"""Scan ingestion service — implements the two-flow branching logic."""

from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.case import Case, CaseStatus
from app.models.camera import Camera
from app.services.eligibility_service import check_eligibility


async def ingest_scan(
    db: Session,
    camera_id_code: str,
    plate: str,
    vin: str,
    latitude: float,
    longitude: float,
    scanned_at: datetime,
    image_url: str | None,
) -> dict:
    """Store the scan and route to the correct flow.

    Returns a dict describing the outcome for the API response.
    """
    camera = (
        db.query(Camera).filter(Camera.camera_code == camera_id_code).first()
    )
    if camera is None:
        raise ValueError(f"Unknown camera: {camera_id_code}")

    tenant_id = camera.tenant_id

    # Always store the scan
    scan = Scan(
        camera_id=camera.id,
        plate=plate,
        vin=vin,
        latitude=latitude,
        longitude=longitude,
        scanned_at=scanned_at,
        image_url=image_url,
        tenant_id=tenant_id,
    )
    db.add(scan)

    # Reuse an open case for this VIN within this tenant.
    open_case = (
        db.query(Case)
        .filter(
            and_(
                Case.vin == vin,
                Case.tenant_id == tenant_id,
                Case.status.in_(
                    (
                        CaseStatus.PENDING_CLAIM.value,
                        CaseStatus.ACTIVE.value,
                    )
                ),
            )
        )
        .order_by(Case.created_at.asc())
        .first()
    )

    if open_case:
        # Every scan is retained, but open cases are not duplicated.
        scan.case_id = open_case.id
        db.commit()
        db.refresh(scan)
        return {
            "scan_id": scan.id,
            "flow": "existing_case",
            "case_id": open_case.id,
            "eligible": None,
            "message": f"Scan linked to existing case {open_case.id}.",
        }

    # New-case flow: check eligibility via mock partner network
    eligible = await check_eligibility(vin)

    if eligible:
        new_case = Case(
            vin=vin,
            plate=plate,
            status=CaseStatus.PENDING_CLAIM.value,
            tenant_id=tenant_id,
            originated_by_tenant_id=tenant_id,
        )
        db.add(new_case)
        db.flush()
        scan.case_id = new_case.id
        db.commit()
        db.refresh(scan)
        db.refresh(new_case)
        return {
            "scan_id": scan.id,
            "flow": "new_case",
            "case_id": new_case.id,
            "eligible": True,
            "message": "Vehicle eligible — new pending_claim case created.",
        }

    # Not eligible — scan stored but no case created
    db.commit()
    db.refresh(scan)
    return {
        "scan_id": scan.id,
        "flow": "new_case",
        "case_id": None,
        "eligible": False,
        "message": "Vehicle not eligible for repossession. Scan stored.",
    }
