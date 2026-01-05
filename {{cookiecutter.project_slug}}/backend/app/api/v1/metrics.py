"""
Simple metrics endpoints for {{cookiecutter.project_name}}.
"""

from typing import Any, Dict

from app.config import Settings, get_settings
from app.models.base import StatusResponse
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_application_metrics(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Get basic application metrics.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy"
    }


@router.get("/summary")
async def get_metrics_summary(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Get a summary of key application metrics.
    """
    return {
        "service": settings.app_name,
        "status": "healthy",
        "version": settings.app_version
    }
