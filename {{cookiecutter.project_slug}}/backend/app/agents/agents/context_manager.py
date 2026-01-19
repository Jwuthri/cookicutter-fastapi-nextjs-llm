"""Context manager agent for managing LLM context limits."""
from typing import List, Dict, Any
from dataclasses import dataclass

# Note: create_agent will be available in future LangChain versions
# For now, we'll use direct LLM calls with structured outputs
from langchain_core.prompts import ChatPromptTemplate

from app.agents.structured_output.context_manager import (
    ContextCheckResult,
    ContextReductionStrategy,
    ContextReductionResult,
)
from app.agents.prompt.context_manager import (
    SYSTEM_PROMPT as CONTEXT_MANAGER_SYSTEM_PROMPT,
    USER_CHECK_CONTEXT_TEMPLATE,
    USER_REDUCE_CONTEXT_TEMPLATE,
)
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger
from app.utils.token_counter import (
    count_tokens_llm,
    get_model_context_limit,
)
from app.config import get_settings

logger = get_logger("context_manager_agent")

settings = get_settings()


@dataclass
class ContextCheckRequest:
    """Request to check context size."""
    system_prompt: str
    history: List[Dict[str, Any]]
    current_item: str
    model_name: str


@dataclass
class ContextReduceRequest:
    """Request to reduce context size."""
    history: List[Dict[str, Any]]
    target_tokens: int
    model_name: str


class ContextManagerAgent:
    """
    Context manager agent for managing LLM context limits.

    This agent:
    1. Checks if context fits within model limits
    2. Decides on reduction strategy (summarize, truncate, hybrid)
    3. Coordinates context reduction when needed
    """

    def __init__(
        self,
        llm_provider: OpenRouterProvider,
        model_name: str = "openai/gpt-4o-mini"
    ):
        """
        Initialize context manager agent.

        Args:
            llm_provider: OpenRouter provider instance
            model_name: Model name for context management decisions
        """
        self.llm_provider = llm_provider
        self.model_name = model_name

        # Initialize LLM
        self.base_llm = llm_provider.get_llm(model_name=model_name, temperature=0)
        
        # Create prompt template for context checking
        self.check_prompt = ChatPromptTemplate.from_messages([
            ("system", CONTEXT_MANAGER_SYSTEM_PROMPT),
            ("user", USER_CHECK_CONTEXT_TEMPLATE)
        ])
        
        # Create prompt template for strategy decision
        self.strategy_prompt = ChatPromptTemplate.from_messages([
            ("system", CONTEXT_MANAGER_SYSTEM_PROMPT),
            ("user", USER_REDUCE_CONTEXT_TEMPLATE)
        ])

        logger.info(f"[ContextManagerAgent] Initialized with model: {model_name}")

    def get_model_context_size(self, model_name: str) -> int:
        """Get context size for a model from OpenRouter API."""
        context_limit = get_model_context_limit(self.llm_provider, model_name)
        return context_limit or getattr(settings, 'default_context_size', 32000)

    def get_safe_limit(self, model_name: str) -> int:
        """Get safe context limit (with buffer)."""
        buffer = getattr(settings, 'context_buffer', 2048)
        return self.get_model_context_size(model_name) - buffer

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using proper token counter."""
        return count_tokens_llm(self.base_llm, text)

    def count_history_tokens(self, history: List[Dict[str, Any]]) -> int:
        """Count total tokens in history items."""
        total = 0
        for item in history:
            # Count tokens in all string fields
            if isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, str):
                        total += self.count_tokens(value)
            elif isinstance(item, str):
                total += self.count_tokens(item)
        return total

    def check_context(
        self,
        request: ContextCheckRequest
    ) -> ContextCheckResult:
        """
        Check if context fits within model limits.

        Args:
            request: Context check request

        Returns:
            ContextCheckResult with token counts and limit status
        """
        # Count tokens
        system_tokens = self.count_tokens(request.system_prompt)
        history_tokens = self.count_history_tokens(request.history)
        current_tokens = self.count_tokens(request.current_item)
        total_tokens = system_tokens + history_tokens + current_tokens

        # Get limits
        context_limit = self.get_model_context_size(request.model_name)
        safe_limit = self.get_safe_limit(request.model_name)
        exceeds_limit = total_tokens > safe_limit

        result = ContextCheckResult(
            total_tokens=total_tokens,
            system_prompt_tokens=system_tokens,
            history_tokens=history_tokens,
            current_item_tokens=current_tokens,
            context_limit=context_limit,
            safe_limit=safe_limit,
            exceeds_limit=exceeds_limit
        )

        logger.info(
            f"[ContextManagerAgent] Context check: {total_tokens}/{safe_limit} tokens, "
            f"exceeds: {exceeds_limit}"
        )

        return result

    def decide_reduction_strategy(
        self,
        check_result: ContextCheckResult,
        history_count: int
    ) -> ContextReductionStrategy:
        """
        Decide on context reduction strategy.

        Args:
            check_result: Result from context check
            history_count: Number of items in history

        Returns:
            ContextReductionStrategy decision
        """
        if not check_result.exceeds_limit:
            return ContextReductionStrategy(
                strategy="none",
                reason="Context fits within safe limit"
            )

        # Simple strategy: truncate if too many items, otherwise summarize
        excess_tokens = check_result.total_tokens - check_result.safe_limit
        
        if history_count > 50:
            # Too many items, truncate
            keep_n = max(10, history_count - (excess_tokens // 100))
            return ContextReductionStrategy(
                strategy="truncate",
                keep_last_n=keep_n,
                reason=f"Too many history items ({history_count}), truncating to last {keep_n}"
            )
        else:
            # Fewer items, summarize
            target_tokens = check_result.safe_limit - check_result.system_prompt_tokens - check_result.current_item_tokens
            return ContextReductionStrategy(
                strategy="summarize",
                target_tokens=max(1000, target_tokens),
                reason=f"Summarizing history to fit within {target_tokens} tokens"
            )

    def reduce_context(
        self,
        request: ContextReduceRequest,
        strategy: ContextReductionStrategy
    ) -> ContextReductionResult:
        """
        Reduce context according to strategy.

        Args:
            request: Context reduction request
            strategy: Reduction strategy to apply

        Returns:
            ContextReductionResult with reduction details
        """
        original_tokens = self.count_history_tokens(request.history)
        original_count = len(request.history)

        if strategy.strategy == "none":
            return ContextReductionResult(
                original_tokens=original_tokens,
                reduced_tokens=original_tokens,
                strategy_used="none",
                items_before=original_count,
                items_after=original_count
            )

        elif strategy.strategy == "truncate":
            if strategy.keep_last_n:
                reduced_history = request.history[-strategy.keep_last_n:]
            else:
                reduced_history = request.history[-10:]  # Default: keep last 10
            
            reduced_tokens = self.count_history_tokens(reduced_history)
            
            return ContextReductionResult(
                original_tokens=original_tokens,
                reduced_tokens=reduced_tokens,
                strategy_used="truncate",
                items_before=original_count,
                items_after=len(reduced_history)
            )

        elif strategy.strategy == "summarize":
            # For now, simple truncation as placeholder
            # In production, this would use a summarization agent
            target_items = max(5, original_count // 2)
            reduced_history = request.history[-target_items:]
            reduced_tokens = self.count_history_tokens(reduced_history)
            
            return ContextReductionResult(
                original_tokens=original_tokens,
                reduced_tokens=reduced_tokens,
                strategy_used="summarize",
                items_before=original_count,
                items_after=len(reduced_history)
            )

        else:  # hybrid
            # Combine truncation and summarization
            if strategy.keep_last_n:
                truncated = request.history[-strategy.keep_last_n:]
            else:
                truncated = request.history[-10:]
            
            reduced_tokens = self.count_history_tokens(truncated)
            
            return ContextReductionResult(
                original_tokens=original_tokens,
                reduced_tokens=reduced_tokens,
                strategy_used="hybrid",
                items_before=original_count,
                items_after=len(truncated)
            )
