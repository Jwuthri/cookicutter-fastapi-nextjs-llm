"""
Custom exceptions for {{cookiecutter.project_name}}.

This module provides enhanced exception handling with context, tracing, and structured error details.
For backward compatibility, it re-exports the enhanced exception system from core.exceptions.
"""

# Import enhanced exception system
from app.core.exceptions import (
    # Base classes
    BaseAppException,
    ErrorSeverity,
    ErrorCategory,
    ErrorDetail,
    ErrorContext,
    
    # Specific exceptions
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    ExternalServiceError,
    DatabaseError,
    CacheError,
    ConfigurationError,
    BusinessLogicError,
    
    # Legacy aliases
    LLMError,
    ServiceUnavailableError,
    MessageQueueError,
    
    # Utilities
    ErrorTracker,
    get_error_tracker,
    
    # Exception handlers
    base_app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
    setup_enhanced_exception_handlers
)

from .utils.logging import get_logger

logger = get_logger("exceptions")

# Legacy compatibility function
def setup_exception_handlers(app):
    """Set up exception handlers for the application (legacy compatibility)."""
    setup_enhanced_exception_handlers(app)
