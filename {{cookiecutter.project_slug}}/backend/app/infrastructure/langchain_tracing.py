"""LangChain tracing integration with LangSmith."""
import os
from typing import Optional

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("langchain_tracing")

# Track if we've already initialized to avoid duplicate initialization
_initialized = False


def initialize_langchain_tracing(force: bool = False):
    """
    Initialize LangChain tracing with LangSmith.
    
    LangChain tracing works via environment variables that LangChain automatically
    picks up. This function sets those environment variables from application settings.
    
    Configure via settings:
    - langchain_tracing_v2: Enable/disable LangChain tracing (LANGCHAIN_TRACING_V2)
    - langchain_endpoint: LangSmith API endpoint (LANGCHAIN_ENDPOINT)
    - langchain_api_key: LangSmith API key (LANGCHAIN_API_KEY)
    - langchain_project: Project name for traces (LANGCHAIN_PROJECT)
    
    Args:
        force: If True, reinitialize even if already initialized
    
    Returns:
        True if tracing was initialized, False otherwise
        
    Example:
        ```python
        from app.infrastructure.langchain_tracing import initialize_langchain_tracing
        
        # Initialize at app startup (or it will auto-initialize on import)
        initialize_langchain_tracing()
        ```
    """
    global _initialized
    
    # Skip if already initialized (unless forced)
    if _initialized and not force:
        return True
    
    try:
        settings = get_settings()
    except Exception as e:
        logger.debug(f"Settings not available yet: {e}")
        return False
    
    # Check if tracing is enabled
    if not settings.langchain_tracing_v2:
        logger.debug("LangChain tracing is disabled")
        return False
    
    # Validate required settings
    if not settings.langchain_api_key:
        logger.warning(
            "LangChain tracing is enabled but langchain_api_key is not set. "
            "Skipping LangChain tracing initialization."
        )
        return False
    
    if not settings.langchain_project:
        logger.warning(
            "LangChain tracing is enabled but langchain_project is not set. "
            "Using default project name."
        )
        # Use app name as default project if not set
        project_name = settings.app_name or "langchain-project"
    else:
        project_name = settings.langchain_project
    
    try:
        # Set environment variables for LangChain tracing
        # LangChain automatically reads these when making calls
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = project_name
        
        logger.info(
            f"LangChain tracing initialized: endpoint={settings.langchain_endpoint}, "
            f"project={project_name}"
        )
        _initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize LangChain tracing: {e}")
        return False


def disable_langchain_tracing():
    """Disable LangChain tracing by unsetting environment variables."""
    global _initialized
    
    try:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        os.environ.pop("LANGCHAIN_ENDPOINT", None)
        os.environ.pop("LANGCHAIN_API_KEY", None)
        os.environ.pop("LANGCHAIN_PROJECT", None)
        _initialized = False
        logger.info("LangChain tracing disabled")
    except Exception as e:
        logger.warning(f"Failed to disable LangChain tracing: {e}")


# Auto-initialize on module import (works for scripts, CLI, etc.)
# This ensures tracing works even when not running through FastAPI
try:
    initialize_langchain_tracing()
except Exception:
    # Silently fail if settings aren't available yet (e.g., during import)
    # It will be initialized later when settings are loaded
    pass
