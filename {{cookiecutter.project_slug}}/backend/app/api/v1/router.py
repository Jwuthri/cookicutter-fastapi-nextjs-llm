"""
Main API v1 router for {{cookiecutter.project_name}}.
"""

from app.api.v1 import auth, health, metrics
from fastapi import APIRouter

api_router = APIRouter(prefix="/v1")

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics", "monitoring"])
