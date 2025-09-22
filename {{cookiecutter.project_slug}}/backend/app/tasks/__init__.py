"""
Background tasks for {{cookiecutter.project_name}}.
"""

from .llm_tasks import *
from .chat_tasks import *
from .general_tasks import *

__all__ = [
    # LLM tasks
    "generate_completion_async",
    "batch_process_messages",
    "update_embeddings",
    
    # Chat tasks
    "process_chat_message_async", 
    "clean_old_sessions",
    "backup_conversation_history",
    
    # General tasks
    "send_notification",
    "cleanup_expired_cache",
    "health_check_services",
    "generate_report",
]
