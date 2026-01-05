"""LangChain tools for context management agent."""
from typing import List, Dict, Any
from langchain_core.tools import tool


@tool
def summarize_history(history: str, max_length: int = 500) -> str:
    """
    Summarize conversation history to reduce token count.
    
    Args:
        history: The conversation history to summarize
        max_length: Maximum length of the summary in characters
    
    Returns:
        A summarized version of the history
    """
    # This is a placeholder - in production, you would use an LLM to summarize
    # For now, we'll just truncate and add a note
    if len(history) <= max_length:
        return history
    
    truncated = history[:max_length]
    return f"{truncated}... [History truncated for context management]"


@tool
def count_history_items(history: List[Dict[str, Any]]) -> int:
    """
    Count the number of items in conversation history.
    
    Args:
        history: List of conversation items (dicts with role/content)
    
    Returns:
        Number of items in the history
    """
    return len(history)


@tool
def get_recent_items(history: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most recent N items from conversation history.
    
    Args:
        history: List of conversation items
        n: Number of recent items to return (default: 10)
    
    Returns:
        List of the most recent N items
    """
    return history[-n:] if len(history) > n else history


@tool
def estimate_tokens(text: str, model_name: str = "openai/gpt-4o-mini") -> int:
    """
    Estimate token count for a given text.
    
    This is a rough estimation. For accurate counts, use the token counter utility.
    
    Args:
        text: Text to estimate tokens for
        model_name: Model name (for context, not used in estimation)
    
    Returns:
        Estimated token count (rough approximation: ~4 chars per token)
    """
    # Rough estimation: ~4 characters per token
    return len(text) // 4


@tool
def format_history_for_display(history: List[Dict[str, Any]]) -> str:
    """
    Format conversation history as a readable string.
    
    Args:
        history: List of conversation items
    
    Returns:
        Formatted string representation of the history
    """
    formatted = []
    for i, item in enumerate(history, 1):
        role = item.get("role", "unknown")
        content = item.get("content", "")
        formatted.append(f"{i}. [{role.upper()}]: {content[:100]}...")
    
    return "\n".join(formatted)


# List of all tools for easy import
CONTEXT_MANAGER_TOOLS = [
    summarize_history,
    count_history_items,
    get_recent_items,
    estimate_tokens,
    format_history_for_display,
]

__all__ = [
    "summarize_history",
    "count_history_items",
    "get_recent_items",
    "estimate_tokens",
    "format_history_for_display",
    "CONTEXT_MANAGER_TOOLS",
]
