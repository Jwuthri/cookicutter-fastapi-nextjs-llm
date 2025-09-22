"""
Dependency injection for {{cookiecutter.project_name}}.
"""

import asyncio
from typing import Generator, TypeVar, Type
from contextlib import asynccontextmanager

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.core.container import get_container, DIContainer
from app.database.base import get_db, SessionLocal
from app.database.session import get_async_db_session, get_async_db_transaction, get_database_manager
from app.services.redis_client import RedisClient
from app.services.kafka_client import KafkaClient
from app.services.rabbitmq_client import RabbitMQClient
from app.core.memory.base import MemoryInterface
from app.core.llm.factory import get_llm_client
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.database.repositories import (
    UserRepository, 
    ChatSessionRepository, 
    ChatMessageRepository, 
    CompletionRepository,
    ApiKeyRepository,
    TaskResultRepository
)

T = TypeVar("T")


# Request-scoped dependency injection
async def get_scoped_container(request: Request) -> DIContainer:
    """Get request-scoped DI container."""
    if not hasattr(request.state, "container_scope"):
        container = get_container()
        request.state.container_scope = container.scope()
        request.state.scoped_container = await request.state.container_scope.__aenter__()
    
    return request.state.scoped_container


async def get_service(service_type: Type[T], container: DIContainer = Depends(get_scoped_container)) -> T:
    """Generic service resolver."""
    return await container.get_service(service_type)


# Service-specific dependency functions
async def get_redis_client(container: DIContainer = Depends(get_scoped_container)) -> RedisClient:
    """Get Redis client instance."""
    return await container.get_service(RedisClient)


async def get_kafka_client(container: DIContainer = Depends(get_scoped_container)) -> KafkaClient:
    """Get Kafka client instance."""
    return await container.get_service(KafkaClient)


async def get_rabbitmq_client(container: DIContainer = Depends(get_scoped_container)) -> RabbitMQClient:
    """Get RabbitMQ client instance."""
    return await container.get_service(RabbitMQClient)


async def get_memory_store(container: DIContainer = Depends(get_scoped_container)) -> MemoryInterface:
    """Get memory store implementation."""
    return await container.get_service(MemoryInterface)


def get_llm_service(settings: Settings = Depends(get_settings)):
    """Get LLM service instance."""
    return get_llm_client(settings.llm_provider, settings)


async def get_chat_service(container: DIContainer = Depends(get_scoped_container)) -> ChatService:
    """Get Chat service instance."""
    return await container.get_service(ChatService)


async def get_conversation_service(container: DIContainer = Depends(get_scoped_container)) -> ConversationService:
    """Get Conversation service instance."""
    return await container.get_service(ConversationService)


# Repository dependencies
async def get_user_repository(container: DIContainer = Depends(get_scoped_container)) -> UserRepository:
    """Get User repository."""
    return await container.get_service(UserRepository)


async def get_chat_session_repository(container: DIContainer = Depends(get_scoped_container)) -> ChatSessionRepository:
    """Get ChatSession repository."""
    return await container.get_service(ChatSessionRepository)


async def get_chat_message_repository(container: DIContainer = Depends(get_scoped_container)) -> ChatMessageRepository:
    """Get ChatMessage repository."""
    return await container.get_service(ChatMessageRepository)


async def get_completion_repository(container: DIContainer = Depends(get_scoped_container)) -> CompletionRepository:
    """Get Completion repository."""
    return await container.get_service(CompletionRepository)


async def get_api_key_repository(container: DIContainer = Depends(get_scoped_container)) -> ApiKeyRepository:
    """Get ApiKey repository."""
    return await container.get_service(ApiKeyRepository)


async def get_task_result_repository(container: DIContainer = Depends(get_scoped_container)) -> TaskResultRepository:
    """Get TaskResult repository."""
    return await container.get_service(TaskResultRepository)


# Database health check
async def check_database_health(db: Session = Depends(get_db)) -> bool:
    """Check database connectivity."""
    try:
        # Simple query to test database connection
        db.execute("SELECT 1")
        return True
    except Exception:
        return False


# Health check dependencies
async def check_redis_health(redis_client: RedisClient = Depends(get_redis_client)) -> bool:
    """Check Redis health."""
    try:
        return await redis_client.health_check()
    except Exception:
        return False


async def check_kafka_health(kafka_client: KafkaClient = Depends(get_kafka_client)) -> bool:
    """Check Kafka health."""
    try:
        return await kafka_client.health_check()
    except Exception:
        return False


async def check_rabbitmq_health(rabbitmq_client: RabbitMQClient = Depends(get_rabbitmq_client)) -> bool:
    """Check RabbitMQ health."""
    try:
        return await rabbitmq_client.health_check()
    except Exception:
        return False


# Validation dependencies
def validate_session_id(session_id: str) -> str:
    """Validate session ID format."""
    if not session_id or len(session_id) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )
    return session_id


def validate_message_content(message: str, settings: Settings = Depends(get_settings)) -> str:
    """Validate message content."""
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    max_length = getattr(settings, "max_message_length", 2000)
    if len(message) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message too long"
        )
    
    return message.strip()


# Request cleanup middleware
async def cleanup_request_scope(request: Request):
    """Cleanup request-scoped services."""
    if hasattr(request.state, "container_scope"):
        try:
            await request.state.container_scope.__aexit__(None, None, None)
        except Exception as e:
            # Log but don't fail the request
            print(f"Error cleaning up request scope: {e}")


# Cleanup function for startup/shutdown
async def cleanup_services():
    """Clean up all services in DI container."""
    from app.database.session import cleanup_database
    
    # Cleanup DI container first
    container = get_container()
    await container.dispose()
    
    # Cleanup database connections
    await cleanup_database()


# Initialize services
async def initialize_services():
    """Initialize all service connections via DI container."""
    from app.database.session import initialize_database
    
    # Initialize async database first
    try:
        await initialize_database()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Continue with other services even if database fails
    
    # Pre-initialize singleton services
    container = get_container()
    try:
        await container.get_service(RedisClient)
        await container.get_service(KafkaClient) 
        await container.get_service(RabbitMQClient)
    except Exception as e:
        # Clean up on failure
        await container.dispose()
        raise e
