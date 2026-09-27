from app.routes.health import router as health_router
from app.routes.activities import router as activities_router
from app.routes.dashboard import router as dashboard_router
from app.routes.trend import router as trend_router
from app.routes.goal import router as goal_router

__all__ = [
    "health_router",
    "activities_router",
    "dashboard_router",
    "trend_router",
    "goal_router",
]
