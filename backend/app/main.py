from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.activities import router as activities_router
from app.routes.dashboard import router as dashboard_router
from app.routes.trend import router as trend_router
from app.routes.goal import router as goal_router
from app.routes.what_if import router as what_if_router
from app.routes.insights import router as insights_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    init_db()
    yield


app = FastAPI(
    title="PlanetPulse API",
    description="Personal Carbon Emissions Engine and Tracking Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Parse configured CORS origins
configured_origins = [
    origin.strip().rstrip("/")
    for origin in CORS_ORIGINS.split(",")
    if origin.strip()
]
if not configured_origins:
    configured_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    """Root endpoint pointing to API status, health, and interactive docs."""
    return {
        "message": "PlanetPulse API is running",
        "status": "ok",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/health")
@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Combined router to support both /api-prefixed team contract and root paths
api_router = APIRouter()
for child in (
    auth_router,
    activities_router,
    dashboard_router,
    trend_router,
    goal_router,
    what_if_router,
    insights_router,
):
    api_router.include_router(child)

app.include_router(api_router)
app.include_router(api_router, prefix="/api")
