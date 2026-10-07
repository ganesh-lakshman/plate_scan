"""Case service — claim logic and tenant-scoped queries."""

from datetime import datetime, timezone

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.models.case import Case, CaseStatus
from app.models.scan import Scan
from app.models.tenant import Tenant
from app.models.user import User


def claim_case(db: Session, case_id: str, user_id: str, user_tenant_id: str) -> Case:
    """Claim a pending_claim case, assigning it to the caller's tenant and user."""
    case = db.query(Case).filter(Case.id == case_id).with_for_update().first()
    if case is None:
        raise ValueError("Case not found.")
    if case.status != CaseStatus.PENDING_CLAIM.value:
        raise ValueError(
            f"Case cannot be claimed — current status is '{case.status}'. "
            "Only pending_claim cases can be claimed."
        )

    now = datetime.now(timezone.utc)
    case.status = CaseStatus.ACTIVE.value
    case.tenant_id = user_tenant_id
    case.assigned_agent_id = user_id
    case.claimed_at = now

    # Re-associate all scans for this VIN to the claiming tenant and this case
    db.query(Scan).filter(Scan.vin == case.vin).update(
        {"case_id": case.id}, synchronize_session="fetch"
    )

    db.commit()
    db.refresh(case)
    return case


def list_cases(
    db: Session, tenant_id: str, status_filter: str | None = None
) -> list[dict]:
    """Return the caller's tenant's cases plus all pending_claim cases.

    Active/closed cases from other tenants are never returned.
    """
    query = db.query(Case, Tenant.name.label("tenant_name"), User.full_name.label("agent_name")).outerjoin(
        Tenant, Case.tenant_id == Tenant.id
    ).outerjoin(
        User, Case.assigned_agent_id == User.id
    )

    if status_filter:
        if status_filter == CaseStatus.PENDING_CLAIM.value:
            query = query.filter(Case.status == CaseStatus.PENDING_CLAIM.value)
        else:
            query = query.filter(
                and_(Case.tenant_id == tenant_id, Case.status == status_filter)
            )
    else:
        # All of own tenant's cases + all pending_claim from any tenant
        query = query.filter(
            or_(
                Case.tenant_id == tenant_id,
                Case.status == CaseStatus.PENDING_CLAIM.value,
            )
        )

    results = query.order_by(Case.created_at.desc()).all()

    cases = []
    for case, tenant_name, agent_name in results:
        cases.append({
            "id": case.id,
            "vin": case.vin,
            "plate": case.plate,
            "status": case.status,
            "tenant_id": case.tenant_id,
            "assigned_agent_id": case.assigned_agent_id,
            "originated_by_tenant_id": case.originated_by_tenant_id,
            "created_at": case.created_at,
            "claimed_at": case.claimed_at,
            "closed_at": case.closed_at,
            "tenant_name": tenant_name,
            "agent_name": agent_name,
        })
    return cases


def get_case_scans(db: Session, case_id: str, tenant_id: str) -> list[Scan]:
    """Return every scan for a case's VIN, ordered by scanned_at."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise ValueError("Case not found.")

    # Tenant isolation: only allow access if it's your case or pending_claim
    if case.status != CaseStatus.PENDING_CLAIM.value and case.tenant_id != tenant_id:
        raise PermissionError("Access denied — this case belongs to another tenant.")

    scans = (
        db.query(Scan)
        .filter(Scan.vin == case.vin)
        .order_by(Scan.scanned_at.asc())
        .all()
    )
    return scans
