"""Seed script — creates tables, two tenants, users, cameras, and sample data."""

from datetime import datetime, timezone, timedelta

from app.database import engine, SessionLocal, Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.camera import Camera
from app.models.case import Case, CaseStatus
from app.models.scan import Scan
from app.api.deps import hash_password


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Tenant).first():
            print("Database already seeded — skipping.")
            return

        # ── Tenants ──────────────────────────────────────────────
        tenant_a = Tenant(id="tenant-a-001", name="Alpha Recovery Agency")
        tenant_b = Tenant(id="tenant-b-002", name="Bravo Recovery Agency")
        db.add_all([tenant_a, tenant_b])
        db.flush()

        # ── Users (password: "password" for all) ────────────────
        password_hash = hash_password("password")

        user_a1 = User(
            id="user-a1",
            username="alice",
            hashed_password=password_hash,
            full_name="Alice Anderson",
            role="admin",
            tenant_id=tenant_a.id,
        )
        user_a2 = User(
            id="user-a2",
            username="adam",
            hashed_password=password_hash,
            full_name="Adam Archer",
            role="staff",
            tenant_id=tenant_a.id,
        )
        user_b1 = User(
            id="user-b1",
            username="bob",
            hashed_password=password_hash,
            full_name="Bob Baker",
            role="admin",
            tenant_id=tenant_b.id,
        )
        user_b2 = User(
            id="user-b2",
            username="beth",
            hashed_password=password_hash,
            full_name="Beth Brown",
            role="staff",
            tenant_id=tenant_b.id,
        )
        db.add_all([user_a1, user_a2, user_b1, user_b2])
        db.flush()

        # ── Cameras ─────────────────────────────────────────────
        cam_a = Camera(
            id="cam-a-001",
            camera_code="cam_1001",
            tenant_id=tenant_a.id,
            truck_label="Truck A-1",
        )
        cam_b = Camera(
            id="cam-b-001",
            camera_code="cam_2050",
            tenant_id=tenant_b.id,
            truck_label="Truck B-1",
        )
        db.add_all([cam_a, cam_b])
        db.flush()

        # ── Tenant A: existing active case for VIN 1FTFW1E51NFA12345 ──
        case_a = Case(
            id="case-a-active-001",
            vin="1FTFW1E51NFA12345",
            plate="7XYZ123",
            status=CaseStatus.ACTIVE.value,
            tenant_id=tenant_a.id,
            originated_by_tenant_id=tenant_a.id,
            assigned_agent_id=user_a2.id,
            claimed_at=datetime(2026, 8, 15, 10, 0, 0, tzinfo=timezone.utc),
        )
        db.add(case_a)
        db.flush()

        # Older scans for that VIN (location trail)
        base_time = datetime(2026, 8, 20, tzinfo=timezone.utc)
        scan_locations = [
            (33.7490, -84.3880, "https://example.com/scans/img_001.jpg"),
            (33.7550, -84.3900, "https://example.com/scans/img_002.jpg"),
            (33.7600, -84.3950, "https://example.com/scans/img_003.jpg"),
        ]
        for i, (lat, lng, url) in enumerate(scan_locations):
            scan = Scan(
                camera_id=cam_a.id,
                plate="7XYZ123",
                vin="1FTFW1E51NFA12345",
                latitude=lat,
                longitude=lng,
                scanned_at=base_time + timedelta(days=i, hours=i * 3),
                image_url=url,
                tenant_id=tenant_a.id,
                case_id=case_a.id,
            )
            db.add(scan)

        # ── Tenant A: a closed case (so the dashboard shows mixed statuses)
        case_a_closed = Case(
            id="case-a-closed-001",
            vin="WVWZZZ3CZWE123456",
            plate="ABC1234",
            status=CaseStatus.CLOSED.value,
            tenant_id=tenant_a.id,
            originated_by_tenant_id=tenant_a.id,
            assigned_agent_id=user_a1.id,
            claimed_at=datetime(2026, 7, 1, 8, 0, 0, tzinfo=timezone.utc),
            closed_at=datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.add(case_a_closed)

        # ── Tenant B has NO case for VIN 5NPE34AF9KH123456 ─────
        # (a new scan will exercise the new-case flow end-to-end)

        db.commit()
        print("Seed data created successfully!")
        print("  Tenants: Alpha Recovery Agency, Bravo Recovery Agency")
        print("  Users: alice/password (A-admin), adam/password (A-staff),")
        print("         bob/password (B-admin), beth/password (B-staff)")
        print("  Cameras: cam_1001 (Tenant A), cam_2050 (Tenant B)")
        print("  Cases: 1 active + 1 closed (Tenant A)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
