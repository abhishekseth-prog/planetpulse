from fastapi import APIRouter

from controllers.activities import router as activities_router
from controllers.auth import router as auth_router
from controllers.dashboard import router as dashboard_router
from controllers.insights import router as insights_router
from controllers.trend import router as trend_router
from controllers.what_if import router as what_if_router

router = APIRouter()
for child in (auth_router, activities_router, dashboard_router, trend_router, what_if_router, insights_router):
    router.include_router(child)
