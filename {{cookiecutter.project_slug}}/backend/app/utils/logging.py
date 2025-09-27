"""
Logging utilities for {{cookiecutter.project_name}}.
Enhanced with Rich for beautiful console output and JSON for production.
"""

import logging
import logging.config
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import Settings
from pythonjsonlogger import jsonlogger
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

# Global rich console instance
console = Console()

# Install rich traceback for better error display
install_rich_traceback(show_locals=True)

# Global logger instance
_logger: Optional[logging.Logger] = None


class RichCustomFormatter(logging.Formatter):
    """Custom formatter that integrates Rich with standard logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rich_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_suppress=[],
            tracebacks_show_locals=True
        )

    def format(self, record):
        return super().format(record)


class JsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for production logging with DataDog integration."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add DataDog fields
        log_record['dd.service'] = getattr(record, 'dd.service', os.getenv('DD_SERVICE', '{{cookiecutter.project_slug}}'))
        log_record['dd.env'] = getattr(record, 'dd.env', os.getenv('DD_ENV', 'production'))
        log_record['dd.version'] = getattr(record, 'dd.version', os.getenv('DD_VERSION', '{{cookiecutter.version}}'))
        log_record['dd.trace_id'] = getattr(record, 'dd.trace_id', '0')
        log_record['dd.span_id'] = getattr(record, 'dd.span_id', '0')

        # Add extra context
        log_record['service'] = '{{cookiecutter.project_slug}}'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'production')


def get_handlers() -> List[str]:
    """Get appropriate handlers based on environment."""
    environment = os.getenv('ENVIRONMENT', 'production').lower()

    if environment in ['production', 'staging']:
        return ['json_production', 'file']
    else:
        return ['console', 'file']


def get_local_env_loggers() -> Dict[str, Any]:
    """Get environment-specific logger configuration."""
    environment = os.getenv('ENVIRONMENT', 'production').lower()

    loggers = {}

    # Suppress noisy loggers in production
    if environment == 'production':
        loggers.update({
            'urllib3.connectionpool': {'level': 'WARNING'},
            'asyncio': {'level': 'WARNING'},
            'httpx': {'level': 'INFO'},
        })

    return loggers



def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """Set up application logging with Rich for development and JSON for production."""
    global _logger

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Ensure log level is uppercase
    log_level = log_level.upper()

    # Define logging configuration
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": RichCustomFormatter,
                "format": "%(message)s",
                "datefmt": "<%d %b %Y | %H:%M:%S>",
            },
            "json_production": {
                "()": JsonFormatter,
                "format": "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] "
                "[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s "
                "dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s",
                "datefmt": "<%d %b %Y | %H:%M:%S>",
            },
            "file": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "level": log_level,
                "formatter": "console",
                "rich_tracebacks": True,
                "tracebacks_show_locals": environment == "development",
                "show_time": True,
                "show_level": True,
                "show_path": environment == "development",
            },
            "json_production": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json_production",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG" if environment == "development" else "INFO",
                "formatter": "file",
                "filename": "logs/app.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "file",
                "filename": "logs/error.log",
                "maxBytes": 5 * 1024 * 1024,  # 5MB
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": get_handlers() + ["error_file"],
                "level": log_level,
                "propagate": False,
            },
            "app": {
                "handlers": get_handlers() + ["error_file"],
                "level": log_level,
                "propagate": False,
            },
            # Suppress noisy loggers
            "urllib3.connectionpool": {"level": "WARNING"},
            "httpx": {"level": "INFO"},
            "uvicorn": {"level": "INFO"},
            "fastapi": {"level": "INFO"},
        }
    }

    # Add environment-specific logger configuration
    LOGGING_CONFIG["loggers"].update(get_local_env_loggers())

    # Capture warnings
    logging.captureWarnings(True)

    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # Set global logger
    _logger = logging.getLogger("app")


def setup_cli_logging(level: str = "INFO", verbose: bool = False):
    """Set up logging specifically for CLI operations."""
    global _logger

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Determine log level
    if verbose:
        level = "DEBUG"

    # CLI-specific logging configuration
    CLI_LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "cli_console": {
                "()": RichCustomFormatter,
                "format": "%(message)s" if not verbose else "%(name)s - %(message)s",
            },
            "cli_file": {
                "format": "%(asctime)s | %(levelname)-8s | CLI | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "cli_console": {
                "class": "rich.logging.RichHandler",
                "level": level,
                "formatter": "cli_console",
                "rich_tracebacks": True,
                "tracebacks_show_locals": verbose,
                "show_time": False,
                "show_level": True,
                "show_path": verbose,
            },
            "cli_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "cli_file",
                "filename": "logs/cli.log",
                "maxBytes": 5 * 1024 * 1024,  # 5MB
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["cli_console", "cli_file"],
                "level": level,
                "propagate": False,
            },
            "cli": {
                "handlers": ["cli_console", "cli_file"],
                "level": level,
                "propagate": False,
            },
        }
    }

    # Apply CLI configuration
    logging.config.dictConfig(CLI_LOGGING_CONFIG)

    # Set global logger
    _logger = logging.getLogger("cli")


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(f"app.{name}")
    return _logger or logging.getLogger("app")


def get_rich_console() -> Console:
    """Get the global Rich console instance."""
    return console


def print_success(message: str):
    """Print success message with rich formatting."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str):
    """Print error message with rich formatting."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str):
    """Print warning message with rich formatting."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str):
    """Print info message with rich formatting."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_debug(message: str):
    """Print debug message with rich formatting."""
    console.print(f"[dim]🐛 {message}[/dim]")
