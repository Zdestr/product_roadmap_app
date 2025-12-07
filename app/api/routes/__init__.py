# app/api/routes/__init__.py
from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.roadmaps import router as roadmaps_router
from app.api.routes.milestones import router as milestones_router
from app.api.routes.stats import router as stats_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(roadmaps_router)
api_router.include_router(milestones_router)
api_router.include_router(stats_router)
