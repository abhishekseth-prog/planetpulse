"""PlanetPulse API application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.api import router as api_router

app = FastAPI(
    title="PlanetPulse API",
    version="1.0.0",
    description="Activity logging and estimated carbon footprint APIs.",
)
configured_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = (
    [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    if configured_origins.strip()
    else [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:4173", "http://127.0.0.1:4173",
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def home():
    return {"message": "PlanetPulse API is running", "status": "ok"}


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}


# Root paths keep the existing frontend's configured API calls working. The
# /api-prefixed aliases are the documented team contract.
app.include_router(api_router)
app.include_router(api_router, prefix="/api")
