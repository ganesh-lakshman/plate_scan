"""Case endpoints — list, claim, and scan trail."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.case import CaseResponse, CaseClaimResponse
from app.schemas.scan import ScanResponse
from app.services.case_service import claim_case, list_cases, get_case_scans

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseResponse])
def get_cases(
    status: str | None = Query(None, description="Filter by status"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = list_cases(db, tenant_id=current_user.tenant_id, status_filter=status)
    return [CaseResponse(**r) for r in results]


@router.post("/{case_id}/claim", response_model=CaseClaimResponse)
def claim(
    case_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        case = claim_case(
            db,
            case_id=case_id,
            user_id=current_user.user_id,
            user_tenant_id=current_user.tenant_id,
        )
        return CaseClaimResponse(
            id=case.id,
            status=case.status,
            tenant_id=case.tenant_id,
            assigned_agent_id=case.assigned_agent_id,
            claimed_at=case.claimed_at,
            message="Case claimed successfully.",
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{case_id}/scans", response_model=list[ScanResponse])
def case_scans(
    case_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        scans = get_case_scans(
            db, case_id=case_id, tenant_id=current_user.tenant_id
        )
        return [ScanResponse.model_validate(s) for s in scans]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
