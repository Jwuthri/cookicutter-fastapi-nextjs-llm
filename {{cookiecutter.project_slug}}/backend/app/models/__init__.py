"""
Pydantic models for {{cookiecutter.project_name}}.
"""

from .chat import *
from .completion import *
from .base import *
from .user import *
from .api_key import *
from .task import *

__all__ = [
    # Chat models
    "ChatMessage",
    "ChatRequest", 
    "ChatResponse",
    "ChatSession",
    "MessageHistory",
    # Completion models
    "CompletionRequest",
    "CompletionResponse", 
    "StreamingCompletionResponse",
    # User models
    "UserProfile",
    "UserPublicProfile", 
    "UserRegistrationRequest",
    "UserLoginRequest",
    "UserUpdateRequest",
    "PasswordChangeRequest",
    "LoginResponse",
    "UserStats",
    "UserListResponse",
    # Note: API Key and advanced Task models available but not currently used in endpoints
    # Base models
    "HealthResponse",
    "ErrorResponse",
    "EnhancedErrorResponse",
    "SuccessResponse",
    "StatusResponse",
    "APIInfo",
    "PaginatedResponse"
]
