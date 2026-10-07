from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    tenant_id: str
    tenant_name: str
    role: str


class CurrentUser(BaseModel):
    user_id: str
    username: str
    tenant_id: str
    role: str
