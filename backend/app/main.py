"""Plate Scan & Case Matching Service — FastAPI entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth as auth_router
from app.api.v1 import scans as scans_router
from app.api.v1 import cases as cases_router
from app.api.mock import partner_network as mock_router

app = FastAPI(
    title="Plate Scan & Case Matching Service",
    version="1.0.0",
    description="LPR platform for the vehicle-recovery industry — case study",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# v1 API routes
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(scans_router.router, prefix="/api/v1")
app.include_router(cases_router.router, prefix="/api/v1")

# Mock external service
app.include_router(mock_router.router, prefix="/mock")


@app.get("/health")
def health_check():
    return {"status": "ok"}
