"""
CQRS (Command Query Responsibility Segregation) implementation for {{cookiecutter.project_name}}.

This package provides the infrastructure for separating command (write) operations
from query (read) operations, improving performance, scalability, and maintainability.
"""

from .interfaces import (
    ICommand,
    IQuery,
    ICommandHandler,
    IQueryHandler,
    ICommandBus,
    IQueryBus,
    CommandResult,
    QueryResult,
)

from .handlers import (
    BaseCommandHandler,
    BaseQueryHandler,
)

from .bus import (
    CommandBus,
    QueryBus,
    CQRSBus,
)

from .decorators import (
    command_handler,
    query_handler,
    transactional,
    cached_query,
)

from .exceptions import (
    CQRSError,
    CommandHandlerNotFoundError,
    QueryHandlerNotFoundError,
    CommandValidationError,
    QueryValidationError,
)

__all__ = [
    # Interfaces
    "ICommand",
    "IQuery", 
    "ICommandHandler",
    "IQueryHandler",
    "ICommandBus",
    "IQueryBus",
    "CommandResult",
    "QueryResult",
    
    # Base classes
    "BaseCommandHandler",
    "BaseQueryHandler",
    
    # Bus implementations
    "CommandBus",
    "QueryBus", 
    "CQRSBus",
    
    # Decorators
    "command_handler",
    "query_handler",
    "transactional",
    "cached_query",
    
    # Exceptions
    "CQRSError",
    "CommandHandlerNotFoundError",
    "QueryHandlerNotFoundError",
    "CommandValidationError",
    "QueryValidationError",
]
