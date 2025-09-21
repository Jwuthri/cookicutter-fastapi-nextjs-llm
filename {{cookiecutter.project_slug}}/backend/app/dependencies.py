"""
Dependency injection for {{cookiecutter.project_name}}.
"""

from functools import lru_cache
from typing import Generator

from fastapi import Depends, HTTPException, status

from app.config import Settings, get_settings
from app.services.redis_client import RedisClient
from app.services.kafka_client import KafkaClient
from app.services.rabbitmq_client import RabbitMQClient
from app.core.llm.factory import get_llm_client
from app.core.memory.base import MemoryInterface
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.in_memory import InMemoryStore


# Global service instances
_redis_client: RedisClient | None = None
_kafka_client: KafkaClient | None = None
_rabbitmq_client: RabbitMQClient | None = None


@lru_cache()
def get_redis_client() -> RedisClient:
    """Get Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


@lru_cache()
def get_kafka_client() -> KafkaClient:
    """Get Kafka client instance."""
    global _kafka_client
    if _kafka_client is None:
        _kafka_client = KafkaClient()
    return _kafka_client


@lru_cache()
def get_rabbitmq_client() -> RabbitMQClient:
    """Get RabbitMQ client instance."""
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
    return _rabbitmq_client


def get_memory_store(
    settings: Settings = Depends(get_settings),
    redis_client: RedisClient = Depends(get_redis_client)
) -> MemoryInterface:
    """Get memory store implementation."""
    try:
        # Try Redis first
        if redis_client:
            return RedisMemory(redis_client)
    except Exception:
        pass
    
    # Fallback to in-memory
    return InMemoryStore()


def get_llm_service(settings: Settings = Depends(get_settings)):
    """Get LLM service instance."""
    return get_llm_client(settings.llm_provider, settings)


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
    
    if len(message) > settings.get("max_message_length", 2000):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message too long"
        )
    
    return message.strip()


# Cleanup function for startup/shutdown
async def cleanup_services():
    """Clean up service connections."""
    global _redis_client, _kafka_client, _rabbitmq_client
    
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
    
    if _kafka_client:
        await _kafka_client.disconnect()
        _kafka_client = None
    
    if _rabbitmq_client:
        await _rabbitmq_client.disconnect()
        _rabbitmq_client = None


# Initialize services
async def initialize_services():
    """Initialize all service connections."""
    redis_client = get_redis_client()
    kafka_client = get_kafka_client()
    rabbitmq_client = get_rabbitmq_client()
    
    try:
        await redis_client.connect()
        await kafka_client.connect()
        await rabbitmq_client.connect()
    except Exception as e:
        # Clean up on failure
        await cleanup_services()
        raise e
