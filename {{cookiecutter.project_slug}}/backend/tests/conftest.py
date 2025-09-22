"""
Test configuration and fixtures for {{cookiecutter.project_name}} backend tests.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings, get_settings
from app.database.base import Base, get_db
from app.database.repositories import UserRepository, ApiKeyRepository
from app.core.security.auth import get_auth_provider, AuthManager
from app.services.redis_client import RedisClient
from app.core.llm.factory import LLMFactory


# Test settings
class TestSettings(Settings):
    """Test-specific settings."""
    environment: str = "testing"
    database_url: str = "sqlite+aiosqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/15"  # Test DB
    log_level: str = "DEBUG"
    secret_key: str = "test-secret-key-very-long-and-secure-for-testing-purposes"
    celery_task_always_eager: bool = True  # Synchronous for tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Get test settings."""
    return TestSettings()


# Database fixtures
@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_settings, test_db_session) -> Generator[TestClient, None, None]:
    """Create test client with dependency overrides."""
    
    # Override dependencies
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_db] = lambda: test_db_session
    
    # Mock external services
    mock_redis = MagicMock()
    mock_kafka = MagicMock()
    mock_rabbitmq = MagicMock()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


# Repository fixtures
@pytest.fixture
def user_repository() -> UserRepository:
    """Get user repository."""
    return UserRepository()


@pytest.fixture
def api_key_repository() -> ApiKeyRepository:
    """Get API key repository."""
    return ApiKeyRepository()


# Auth fixtures
@pytest.fixture
def auth_manager(test_settings) -> AuthManager:
    """Get auth manager with test settings."""
    return AuthManager(test_settings)


@pytest_asyncio.fixture
async def test_user(test_db_session, user_repository) -> dict:
    """Create a test user."""
    from app.database.models import UserStatusEnum
    
    user = user_repository.create(
        db=test_db_session,
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8OdTxhwKhO",  # "testpass123"
        full_name="Test User",
        is_active=True,
        status=UserStatusEnum.ACTIVE
    )
    
    await test_db_session.commit()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }


@pytest_asyncio.fixture
async def admin_user(test_db_session, user_repository) -> dict:
    """Create a test admin user."""
    from app.database.models import UserStatusEnum
    
    user = user_repository.create(
        db=test_db_session,
        username="admin",
        email="admin@example.com", 
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8OdTxhwKhO",  # "testpass123"
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        status=UserStatusEnum.ACTIVE
    )
    
    await test_db_session.commit()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }


@pytest.fixture
def auth_headers(auth_manager, test_user) -> dict:
    """Create auth headers with JWT token."""
    token_data = {
        "sub": str(test_user["id"]),
        "username": test_user["username"],
        "email": test_user["email"]
    }
    token = auth_manager.create_access_token(token_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(auth_manager, admin_user) -> dict:
    """Create admin auth headers with JWT token."""
    token_data = {
        "sub": str(admin_user["id"]),
        "username": admin_user["username"],
        "email": admin_user["email"],
        "is_superuser": True
    }
    token = auth_manager.create_access_token(token_data)
    
    return {"Authorization": f"Bearer {token}"}


# Mock service fixtures
@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    mock = MagicMock()
    mock.generate_completion.return_value = {
        "choices": [{
            "text": "This is a test response from the mock LLM.",
            "finish_reason": "stop"
        }],
        "usage": {
            "total_tokens": 20,
            "prompt_tokens": 10,
            "completion_tokens": 10
        }
    }
    return mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock = MagicMock()
    mock.set.return_value = True
    mock.get.return_value = None
    mock.delete.return_value = 1
    mock.exists.return_value = False
    return mock


# Test data fixtures
@pytest.fixture
def sample_chat_request() -> dict:
    """Sample chat request data."""
    return {
        "message": "Hello, how are you?",
        "session_id": None,
        "context": {"user_preference": "casual"}
    }


@pytest.fixture
def sample_completion_request() -> dict:
    """Sample completion request data."""
    return {
        "prompt": "Complete this sentence: The weather today is",
        "max_tokens": 50,
        "temperature": 0.7,
        "model": "gpt-4o-mini"
    }


# Async test helpers
@pytest.fixture
def async_client(client):
    """Async version of test client."""
    return client


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Cleanup code here if needed
    pass


# Parametrized fixtures for testing different scenarios
@pytest.fixture(params=["development", "production", "testing"])
def environment_setting(request):
    """Test different environment settings."""
    return request.param


@pytest.fixture(params=[True, False])
def feature_flag(request):
    """Test with feature flags on/off."""
    return request.param
