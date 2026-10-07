# Design Notes — Plate Scan & Case Matching Service

## 1. Database Schema (ER Diagram)

```
┌─────────────────┐       ┌─────────────────────┐       ┌──────────────────────┐
│     tenants      │       │       users          │       │      cameras         │
├─────────────────┤       ├─────────────────────┤       ├──────────────────────┤
│ id          PK  │◄──┐   │ id             PK   │       │ id              PK   │
│ name            │   ├───│ tenant_id      FK   │   ┌───│ tenant_id       FK   │
│ created_at      │   │   │ username   UNIQUE   │   │   │ camera_code  UNIQUE  │
└─────────────────┘   │   │ hashed_password     │   │   │ truck_label          │
                      │   │ full_name           │   │   │ created_at           │
                      │   │ role                │   │   └──────────────────────┘
                      │   │ created_at          │   │              │
                      │   └─────────────────────┘   │              │
                      │              │              │              │
                      │              │              │              │
┌─────────────────────┴──────────────┴──┐   ┌──────┴──────────────┴────────────┐
│             cases                     │   │            scans                 │
├───────────────────────────────────────┤   ├──────────────────────────────────┤
│ id                         PK         │   │ id                    PK         │
│ vin                                   │   │ camera_id             FK ────────┤
│ plate                                 │   │ plate                            │
│ status (pending_claim|active|closed)  │   │ vin                              │
│ tenant_id                  FK ────────┤   │ latitude                         │
│ assigned_agent_id          FK ────────┤   │ longitude                        │
│ originated_by_tenant_id    FK ────────┤   │ scanned_at                       │
│ created_at                            │   │ image_url                        │
│ claimed_at                            │   │ tenant_id             FK ────────┤
│ closed_at                             │   │ case_id               FK ────────┤
└───────────────────────────────────────┘   │ created_at                       │
                                            └──────────────────────────────────┘
```

### Key Indexes
| Table  | Index | Purpose |
|--------|-------|---------|
| cases  | `ix_cases_tenant_status (tenant_id, status)` | Tenant-scoped case listing |
| cases  | `ix_cases_vin_status (vin, status)` | Fast VIN-based lookup during scan ingest |
| scans  | `ix_scans_vin_scanned_at (vin, scanned_at)` | Location trail ordered by time |
| scans  | `ix_scans_tenant_vin (tenant_id, vin)` | Tenant-scoped scan lookup |
| cameras | `ix_cameras_camera_code (camera_code)` UNIQUE | Resolve tenant from camera webhook |

---

## 2. Multi-Tenancy & Access Control

### Approach: Shared-schema, row-level tenant isolation

Every row that belongs to a tenant carries a `tenant_id` foreign key. All authenticated queries filter by the caller's `tenant_id` before returning data.

### How each endpoint enforces boundaries

| Endpoint | Auth | Tenant Rule |
|----------|------|-------------|
| `POST /api/v1/scans` | None (camera webhook) | Tenant resolved from `camera_id`. A camera belongs to exactly one tenant, so the scan is automatically attributed. |
| `GET /api/v1/cases` | JWT required | Returns own tenant's cases (all statuses) **plus** `pending_claim` from any tenant. Active/closed from other tenants never appear. |
| `POST /api/v1/cases/{id}/claim` | JWT required | Any authenticated user can claim a `pending_claim` case. Claiming assigns it to the **caller's** tenant and sets the caller as agent. SELECT … FOR UPDATE prevents race conditions. |
| `GET /api/v1/cases/{id}/scans` | JWT required | Allowed if the case belongs to the caller's tenant or if the case is `pending_claim`. Other tenants' active/closed cases are rejected with 403. |

### Authentication

Simplified JWT-based auth (username + password → JWT). In production this would be replaced by an identity provider (e.g. AWS Cognito, Auth0).

---

## 3. AWS Deployment Sketch

### Architecture

```
                  ┌─────────────────┐
   Internet ──►  │  CloudFront CDN  │  ◄── React SPA (S3 bucket)
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │   ALB (HTTPS)   │
                  └────────┬────────┘
                           │
              ┌────────────▼────────────┐
              │  ECS Fargate (FastAPI)  │  ◄── 2+ tasks, auto-scaling
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   RDS PostgreSQL        │  ◄── Multi-AZ, encrypted
              │   (db.r6g.large)        │
              └─────────────────────────┘
```

### Services & Rationale

| Component | AWS Service | Why |
|-----------|-------------|-----|
| **Frontend** | S3 + CloudFront | Static SPA; global CDN; cheap |
| **API** | ECS Fargate | Serverless containers; no EC2 patching; scales to zero-ish |
| **Database** | RDS PostgreSQL | Managed; Multi-AZ; automated backups; read replicas if needed |
| **Auth** | Cognito (or ALB OIDC) | Managed user pools per tenant; JWT validation at ALB |
| **Secrets** | Secrets Manager | DB creds, JWT signing key |
| **CI/CD** | CodePipeline + ECR | Push image → deploy to Fargate |

### Scaling considerations

- **Read replicas** for heavy GET queries (scans trail).
- **Connection pooling** via PgBouncer sidecar in ECS.
- **Caching**: Redis (ElastiCache) for hot case lookups.
- **Async ingest**: For high camera throughput, front the scan endpoint with SQS → Lambda workers.
- **Partitioning**: As scan volume grows, partition the `scans` table by `scanned_at` (time-range) for efficient pruning and querying.

---

## 4. What's Incomplete / Next Steps

- **Real auth provider** — replace hardcoded users with Cognito / OIDC.
- **Notifications** — use SNS or WebSockets (Pusher / API Gateway WS) to push real-time alerts when a scan matches, or a case is claimed.
- **Image storage** — upload to S3, store the S3 key instead of a URL string.
- **Pagination** — scan trails and case lists should be paginated (offset/cursor-based).
- **Audit log** — every claim / status change logged for compliance.
- **Rate limiting** — the unauthenticated scan endpoint needs throttling (API Gateway throttling or middleware).
- **Map view** — plot scan coordinates on a Leaflet/Mapbox map in the frontend.
