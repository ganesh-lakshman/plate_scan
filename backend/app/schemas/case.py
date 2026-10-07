from datetime import datetime
from pydantic import BaseModel


class CaseResponse(BaseModel):
    id: str
    vin: str
    plate: str | None
    status: str
    tenant_id: str
    assigned_agent_id: str | None
    originated_by_tenant_id: str
    created_at: datetime
    claimed_at: datetime | None
    closed_at: datetime | None
    tenant_name: str | None = None
    agent_name: str | None = None

    model_config = {"from_attributes": True}


class CaseClaimRequest(BaseModel):
    pass  # no body needed; user comes from auth token


class CaseClaimResponse(BaseModel):
    id: str
    status: str
    tenant_id: str
    assigned_agent_id: str
    claimed_at: datetime
    message: str
