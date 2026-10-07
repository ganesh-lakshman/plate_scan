"""Mock partner-network eligibility endpoint (Appendix A)."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/partner-network", tags=["mock"])


class EligibilityRequest(BaseModel):
    vin: str


class EligibilityResponse(BaseModel):
    vin: str
    still_eligible_for_repo: bool


@router.post("/eligibility", response_model=EligibilityResponse)
def check_eligibility(body: EligibilityRequest):
    """Trivial stub: eligible unless VIN ends with '00000'."""
    eligible = not body.vin.endswith("00000")
    return EligibilityResponse(vin=body.vin, still_eligible_for_repo=eligible)
