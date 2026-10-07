"""Auth endpoints — simple login for the case study."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import LoginRequest, TokenResponse
from app.api.deps import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    token = create_access_token({"sub": user.id})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        tenant_id=user.tenant_id,
        tenant_name=tenant.name if tenant else "",
        role=user.role,
    )
