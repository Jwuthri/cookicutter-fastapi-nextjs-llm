"""
Base models for {{cookiecutter.project_name}}.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Literal


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(default=None, description="Service version")
    environment: Optional[str] = Field(default=None, description="Environment")
    services: Optional[Dict[str, str]] = Field(default=None, description="Individual service statuses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00.000Z",
                "service": "{{cookiecutter.project_name}}",
                "version": "{{cookiecutter.version}}",
                "environment": "development",
                "services": {
                    "redis": "healthy",
                    "kafka": "healthy", 
                    "rabbitmq": "healthy"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracking")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "The message field is required",
                "details": {"field": "message", "code": "required"},
                "request_id": "req_123456789",
                "timestamp": "2024-01-01T12:00:00.000Z"
            }
        }


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Items skipped")
    has_more: bool = Field(..., description="Whether there are more items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "limit": 50,
                "offset": 0,
                "has_more": True
            }
        }


class APIInfo(BaseModel):
    """API information model."""
    
    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    docs_url: str = Field(..., description="Documentation URL")
    health_url: str = Field(..., description="Health check URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "{{cookiecutter.project_name}} API",
                "version": "{{cookiecutter.version}}",
                "description": "{{cookiecutter.description}}",
                "docs_url": "/docs",
                "health_url": "/health"
            }
        }
