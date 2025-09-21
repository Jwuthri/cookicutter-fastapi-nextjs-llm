"""
Logging utilities for {{cookiecutter.project_name}}.
"""

import sys
from loguru import logger
from app.config import Settings, get_settings


def setup_logging(settings: Settings):
    """Set up application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Add custom handler with formatting
    logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file handler for production
    if settings.environment == "production":
        logger.add(
            "logs/app.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="gz"
        )


def get_logger(name: str):
    """Get a logger instance."""
    return logger.bind(name=name)
