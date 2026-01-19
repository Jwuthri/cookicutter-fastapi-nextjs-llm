"""Structured output models for context management."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ContextCheckResult(BaseModel):
    """Result of context length check."""

    total_tokens: int = Field(description="Total token count")
    system_prompt_tokens: int = Field(description="System prompt token count")
    history_tokens: int = Field(description="History token count")
    current_item_tokens: int = Field(description="Current item token count")
    context_limit: int = Field(description="Model context limit")
    safe_limit: int = Field(description="Safe limit (context_limit - buffer)")
    exceeds_limit: bool = Field(description="Whether context exceeds safe limit")


class ContextReductionStrategy(BaseModel):
    """Context reduction strategy decision."""

    strategy: Literal["none", "summarize", "truncate", "hybrid"] = Field(
        description="Reduction strategy to use"
    )
    keep_last_n: Optional[int] = Field(
        default=None, description="Number of items to keep (for truncate)"
    )
    target_tokens: Optional[int] = Field(
        default=None, description="Target token count (for summarize)"
    )
    reason: str = Field(description="Explanation of the decision")


class ContextReductionResult(BaseModel):
    """Result of context reduction."""

    original_tokens: int = Field(description="Original token count")
    reduced_tokens: int = Field(description="Token count after reduction")
    strategy_used: str = Field(description="Strategy that was applied")
    items_before: int = Field(description="Number of items before reduction")
    items_after: int = Field(description="Number of items after reduction")
