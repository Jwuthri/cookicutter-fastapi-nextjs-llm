"""
Database package for {{cookiecutter.project_name}}.
"""

from .base import Base, SessionLocal, engine, get_db
from .models import *
from .repositories import *

__all__ = [
    # Database core
    "Base",
    "get_db",
    "engine",
    "SessionLocal",

    # Database models
    "User",
    "ChatSession",
    "ChatMessage",
    "Completion",
    "ApiKey",
    "TaskResult",

    # Enums
    "UserStatusEnum",
    "MessageRoleEnum",

    # Repositories
    "UserRepository",
    "ChatSessionRepository",
    "ChatMessageRepository",
    "CompletionRepository",
    "ApiKeyRepository",
    "TaskResultRepository",

    # Utilities
    "ModelConverter",
]
