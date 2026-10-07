# Plate Scan & Case Matching Service

A full-stack service for the vehicle-recovery (repossession) industry. Ingests license plate scans from truck-mounted cameras, matches them against cases, and exposes a tenant-scoped dashboard.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 16 |
| Frontend | React 18, TypeScript, Vite, React Router |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Containerization | Docker, Docker Compose |

## Quick Start (Docker Compose)

```bash
# Clone the repo
git clone <repo-url> && cd veh_rec

# Start everything (PostgreSQL + Backend + Frontend)
docker compose up --build

# In a new terminal — seed the database
docker compose exec backend python -m app.seed
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## Quick Start (Without Docker)

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL running locally

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Create the database (make sure PostgreSQL is running)
# createdb plate_scan_db   OR via psql: CREATE DATABASE plate_scan_db;

# Seed data
python -m app.seed

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Seed Users

| Username | Password | Tenant | Role |
|----------|----------|--------|------|
| alice | password | Alpha Recovery Agency | admin |
| adam | password | Alpha Recovery Agency | staff |
| bob | password | Bravo Recovery Agency | admin |
| beth | password | Bravo Recovery Agency | staff |

## API Endpoints

### Unauthenticated
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/scans` | Ingest a scan (camera webhook) |
| POST | `/mock/partner-network/eligibility` | Mock eligibility check |

### Authenticated (JWT Bearer)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login → JWT token |
| GET | `/api/v1/cases` | List cases (own tenant + pending_claim) |
| GET | `/api/v1/cases?status=pending_claim` | Filter by status |
| POST | `/api/v1/cases/{case_id}/claim` | Claim a pending_claim case |
| GET | `/api/v1/cases/{case_id}/scans` | Get scan/location trail |

## Demo Walkthrough

### 1. Existing-case flow
Tenant A already has an active case for VIN `1FTFW1E51NFA12345`. Submit a new scan from camera `cam_1001`:

```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "cam_1001",
    "plate": "7XYZ123",
    "vin": "1FTFW1E51NFA12345",
    "latitude": 33.7700,
    "longitude": -84.4000,
    "scanned_at": "2026-09-01T14:32:00Z",
    "image_url": "https://example.com/scans/img_new.jpg"
  }'
```

The response shows `"flow": "existing_case"` — the scan is linked to the existing active case.

### 2. New-case flow
Tenant B has NO case for VIN `5NPE34AF9KH123456`. Submit a scan from camera `cam_2050`:

```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "cam_2050",
    "plate": "8ABC456",
    "vin": "5NPE34AF9KH123456",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "scanned_at": "2026-09-02T09:15:00Z",
    "image_url": "https://example.com/scans/img_new2.jpg"
  }'
```

The response shows `"flow": "new_case"` with a new pending_claim case.

### 3. Cross-tenant claim
Log in as alice (Tenant A) and claim the case that Tenant B's camera created:

```bash
# Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"password"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Claim the pending case (use the case_id from step 2)
curl -X POST http://localhost:8000/api/v1/cases/<case_id>/claim \
  -H "Authorization: Bearer $TOKEN"
```

## Assumptions

1. **VIN is the primary vehicle identifier** — the case-matching logic branches on VIN, not plate (plates can change).
2. **One open case per VIN per tenant** — pending and active cases are reused by later scans for that tenant and VIN. Each scan event is still stored separately and linked to that case.
3. **Pending cases are visible cross-tenant** — the document says any user can claim; visibility is a prerequisite.
4. **Claiming re-assigns tenant** — when Tenant A claims a case originated by Tenant B, the case moves to Tenant A. The `originated_by_tenant_id` preserves origin lineage.
5. **Scans are linked to cases after claim** — when a case is claimed, all prior scans for that VIN are associated with the case.
6. **Auth is simplified** — hardcoded bcrypt passwords; JWT with no refresh flow. Production would use Cognito/OIDC.

## Project Structure

```
veh_rec/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── mock/          # Mock eligibility endpoint
│   │   │   └── v1/            # Versioned API routes
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer
│   │   ├── config.py          # Settings (env-based)
│   │   ├── database.py        # DB engine & session
│   │   ├── main.py            # FastAPI app entry point
│   │   └── seed.py            # Seed data script
│   ├── alembic/               # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── context/           # React context (auth state)
│   │   ├── pages/             # Route-level page components
│   │   └── services/          # API client (axios)
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── DESIGN.md                  # Schema, multi-tenancy & AWS notes
└── README.md
```
