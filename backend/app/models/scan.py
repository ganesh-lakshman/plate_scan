import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    camera_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cameras.id"), nullable=False, index=True
    )
    plate: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    case_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("cases.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    camera = relationship("Camera", back_populates="scans")
    case = relationship("Case")

    __table_args__ = (
        Index("ix_scans_vin_scanned_at", "vin", "scanned_at"),
        Index("ix_scans_tenant_vin", "tenant_id", "vin"),
    )
