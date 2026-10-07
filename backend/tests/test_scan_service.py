import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.database import Base
from app.models.camera import Camera
from app.models.case import Case, CaseStatus
from app.models.scan import Scan
from app.models.tenant import Tenant
from app.services.scan_service import ingest_scan


class IngestScanTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.tenant = Tenant(name="Test tenant")
        self.db.add(self.tenant)
        self.db.flush()
        self.camera = Camera(
            camera_code="test-camera",
            tenant_id=self.tenant.id,
            truck_label="Test truck",
        )
        self.db.add(self.camera)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    async def ingest(self):
        return await ingest_scan(
            db=self.db,
            camera_id_code=self.camera.camera_code,
            plate="8ABC456",
            vin="5NPE34AF9KH123456",
            latitude=34.0522,
            longitude=-118.2437,
            scanned_at=datetime(2026, 9, 2, 9, 15, tzinfo=timezone.utc),
            image_url="https://example.com/scans/img_new2.jpg",
        )

    async def test_repeated_scan_reuses_pending_case_and_stores_each_scan(self):
        case = Case(
            vin="5NPE34AF9KH123456",
            plate="8ABC456",
            status=CaseStatus.PENDING_CLAIM.value,
            tenant_id=self.tenant.id,
            originated_by_tenant_id=self.tenant.id,
        )
        self.db.add(case)
        self.db.commit()

        with patch(
            "app.services.scan_service.check_eligibility",
            new_callable=AsyncMock,
        ) as check_eligibility:
            first_result = await self.ingest()
            second_result = await self.ingest()

        self.assertEqual(first_result["case_id"], case.id)
        self.assertEqual(second_result["case_id"], case.id)
        self.assertEqual(first_result["flow"], "existing_case")
        self.assertNotEqual(first_result["scan_id"], second_result["scan_id"])
        self.assertEqual(self.db.query(Case).count(), 1)
        self.assertEqual(self.db.query(Scan).count(), 2)
        self.assertEqual(
            self.db.query(Scan.case_id).distinct().all(),
            [(case.id,)],
        )
        check_eligibility.assert_not_awaited()

    async def test_first_eligible_scan_creates_pending_case(self):
        with patch(
            "app.services.scan_service.check_eligibility",
            new_callable=AsyncMock,
            return_value=True,
        ):
            first_result = await self.ingest()
            second_result = await self.ingest()

        self.assertEqual(first_result["flow"], "new_case")
        self.assertEqual(second_result["flow"], "existing_case")
        self.assertEqual(first_result["case_id"], second_result["case_id"])
        self.assertEqual(self.db.query(Case).count(), 1)
        self.assertEqual(self.db.query(Scan).count(), 2)
