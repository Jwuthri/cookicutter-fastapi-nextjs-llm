"""
Example use case: Using the Context Manager Agent.

This example demonstrates:
1. Setting up the context manager agent
2. Checking context limits
3. Deciding on reduction strategy
4. Reducing context when needed
"""

from app.agents.agents.context_manager import (
    ContextManagerAgent,
    ContextCheckRequest,
    ContextReduceRequest,
)
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger

logger = get_logger("agent_example")


def context_manager_example():
    """Example of using the context manager agent."""
    # Initialize provider
    provider = OpenRouterProvider()
    
    # Create context manager agent
    agent = ContextManagerAgent(
        llm_provider=provider,
        model_name="openai/gpt-4o-mini"
    )
    
    # Example system prompt
    system_prompt = "You are a helpful assistant."
    
    # Example history (simulated conversation items)
    history = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language..."},
        # ... more items
    ]
    
    # Current item to add
    current_item = "Can you explain machine learning?"
    
    # Check context
    check_request = ContextCheckRequest(
        system_prompt=system_prompt,
        history=history,
        current_item=current_item,
        model_name="openai/gpt-4o-mini"
    )
    
    check_result = agent.check_context(check_request)
    
    logger.info(f"Total tokens: {check_result.total_tokens}")
    logger.info(f"Safe limit: {check_result.safe_limit}")
    logger.info(f"Exceeds limit: {check_result.exceeds_limit}")
    
    # If exceeds limit, decide on strategy
    if check_result.exceeds_limit:
        strategy = agent.decide_reduction_strategy(
            check_result,
            len(history)
        )
        
        logger.info(f"Strategy: {strategy.strategy}")
        logger.info(f"Reason: {strategy.reason}")
        
        # Reduce context
        reduce_request = ContextReduceRequest(
            history=history,
            target_tokens=check_result.safe_limit - check_result.system_prompt_tokens - check_result.current_item_tokens,
            model_name="openai/gpt-4o-mini"
        )
        
        reduction_result = agent.reduce_context(reduce_request, strategy)
        
        logger.info(f"Original tokens: {reduction_result.original_tokens}")
        logger.info(f"Reduced tokens: {reduction_result.reduced_tokens}")
        logger.info(f"Items before: {reduction_result.items_before}")
        logger.info(f"Items after: {reduction_result.items_after}")
    
    return check_result


if __name__ == "__main__":
    logger.info("=== Context Manager Agent Example ===")
    context_manager_example()
