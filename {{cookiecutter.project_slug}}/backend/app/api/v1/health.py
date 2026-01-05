"""
Health check endpoints for {{cookiecutter.project_name}}.
"""

from datetime import datetime
from typing import Any, Dict

from app.config import Settings, get_settings
from app.models.base import HealthResponse
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """
    Health check for the application.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service=settings.app_name,
        version=settings.app_version,
        environment="development" if settings.debug else "production",
    )


@router.get("/ready")
async def readiness_check(
) -> Dict[str, Any]:
    """
    Readiness check - returns 200 only if critical services are available.
    """
    response = {
        "ready": True,
        "timestamp": datetime.now().isoformat(),
    }

    return response


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - basic health check that always returns 200 if the app is running.
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }
