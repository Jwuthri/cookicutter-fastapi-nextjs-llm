"""
Middleware package for {{cookiecutter.project_name}}.
"""

from .tracing_middleware import (
    DatabaseTracingMixin,
    ExternalServiceTracingMixin,
    TracingMiddleware,
)

# Import setup_middleware from the parent middleware module
from ..middleware import setup_middleware

__all__ = [
    "TracingMiddleware",
    "DatabaseTracingMixin",
    "ExternalServiceTracingMixin",
    "setup_middleware",
]
