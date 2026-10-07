from datetime import datetime
from pydantic import BaseModel


class ScanIngest(BaseModel):
    """Payload from a camera webhook — unauthenticated."""
    camera_id: str
    plate: str
    vin: str
    latitude: float
    longitude: float
    scanned_at: datetime
    image_url: str | None = None


class ScanResponse(BaseModel):
    id: str
    camera_id: str
    plate: str
    vin: str
    latitude: float
    longitude: float
    scanned_at: datetime
    image_url: str | None
    tenant_id: str
    case_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScanIngestResult(BaseModel):
    scan_id: str
    flow: str  # "existing_case" or "new_case"
    case_id: str | None = None
    eligible: bool | None = None
    message: str
