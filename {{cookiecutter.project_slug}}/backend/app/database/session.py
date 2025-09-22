"""
Async database session management for {{cookiecutter.project_name}}.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import Session
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("database_session")

# Global async engine and session factory
_async_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_database_url(database_url: str) -> str:
    """Convert sync database URL to async."""
    if database_url.startswith("sqlite:///"):
        # SQLite: replace sqlite:// with sqlite+aiosqlite://
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    elif database_url.startswith("postgresql://"):
        # PostgreSQL: replace postgresql:// with postgresql+asyncpg://
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        # Assume it's already async-compatible
        return database_url


def create_async_database_engine() -> AsyncEngine:
    """Create async database engine with proper configuration."""
    settings = get_settings()
    
    if not settings.database_url:
        # In-memory SQLite for testing
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=settings.environment == "development",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            future=True
        )
    
    database_url = get_async_database_url(settings.database_url)
    
    if database_url.startswith("sqlite"):
        # SQLite configuration
        return create_async_engine(
            database_url,
            echo=settings.environment == "development",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            future=True
        )
    elif database_url.startswith("postgresql"):
        # PostgreSQL configuration
        return create_async_engine(
            database_url,
            echo=settings.environment == "development",
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,  # 1 hour
            future=True
        )
    else:
        # Generic configuration
        return create_async_engine(
            database_url,
            echo=settings.environment == "development",
            future=True
        )


def get_async_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_database_engine()
        logger.info("Async database engine created")
    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_async_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        logger.info("Async session factory created")
    return _async_session_factory


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with automatic cleanup."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with explicit transaction management."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            await session.begin()
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseManager:
    """Centralized database management for async operations."""
    
    def __init__(self):
        self.engine = get_async_engine()
        self.session_factory = get_async_session_factory()
    
    async def create_tables(self):
        """Create all database tables asynchronously."""
        from app.database.base import Base
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables asynchronously."""
        from app.database.base import Base
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped successfully")
    
    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# FastAPI dependency for async sessions
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions."""
    async with get_async_session() as session:
        yield session


async def get_async_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database transactions."""
    async with get_async_transaction() as session:
        yield session


# Event listeners for SQLite optimization
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set journal mode to WAL for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set temp store to memory for better performance  
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Set cache size to 64MB
        cursor.execute("PRAGMA cache_size=64000")
        cursor.close()


# Initialize database on import if needed
async def initialize_database():
    """Initialize database tables and connections."""
    db_manager = get_database_manager()
    
    # Create tables
    await db_manager.create_tables()
    
    # Verify connectivity
    if not await db_manager.health_check():
        raise RuntimeError("Database initialization failed: health check failed")
    
    logger.info("Database initialized successfully")


async def cleanup_database():
    """Cleanup database connections."""
    global _async_engine, _async_session_factory, _db_manager
    
    if _db_manager:
        await _db_manager.close()
        _db_manager = None
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
    
    _async_session_factory = None
    logger.info("Database cleanup completed")
