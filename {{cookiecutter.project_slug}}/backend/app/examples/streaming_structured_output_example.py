"""
Full example: Streaming structured output with LangChain + OpenRouter.

Shows the structured object being built incrementally during streaming,
similar to Agno's approach. Demonstrates both async generator and callback patterns.
"""

import asyncio
import json
from typing import Callable, Optional

from app.agents.agents import CustomerSupportAgent
from app.agents.structured_output.customer_support import CustomerSupportResponse
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger

logger = get_logger("streaming_structured_output_example")


def print_partial_update(response: CustomerSupportResponse, is_complete: bool = False):
    """
    Print partial structured output update (Agno-style).
    
    Shows the structured object being built incrementally.
    """
    if is_complete:
        print("\n" + "=" * 60)
        print("✅ FINAL STRUCTURED OUTPUT:")
        print("=" * 60)
        print(json.dumps(response.model_dump(), indent=2))
    else:
        print("\n📦 PARTIAL UPDATE:")
        print("-" * 40)
        data = response.model_dump()
        
        # Pretty print what we have so far
        for key, value in data.items():
            if isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
                for item in value[:2]:  # Show first 2
                    if isinstance(item, dict):
                        print(f"    - {item.get('name', item)}")
                    else:
                        print(f"    - {item}")
                if len(value) > 2:
                    print(f"    ... and {len(value) - 2} more")
            elif isinstance(value, str) and len(value) > 50:
                print(f"  {key}: {value[:50]}...")
            elif value is not None:
                print(f"  {key}: {value}")


async def streaming_with_callback_example():
    """
    Example using callback pattern (Agno-style).
    
    Shows incremental updates as the structured object is being built.
    """
    print("=" * 60)
    print("STREAMING STRUCTURED OUTPUT DEMO (Callback Pattern)")
    print("=" * 60)
    
    # Initialize provider and agent
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="openai/gpt-4o-mini",
        temperature=0.7
    )
    
    query = (
        "I need help with my order #12345. It hasn't arrived yet and I'm very frustrated! "
        "This is the third time this has happened. I want a refund and to speak to a manager."
    )
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    def stream_callback(response: CustomerSupportResponse):
        """Callback function called on each incremental update."""
        print_partial_update(response, is_complete=False)
    
    # Stream with callback
    result = await agent.handle_inquiry_stream_with_callback(
        customer_message=query,
        callback=stream_callback,
        customer_id="customer_123",
        session_id="streaming-session-456",
        tags=["support", "streaming"],
        metadata={"order_id": "12345"}
    )
    
    # Show final result
    print_partial_update(result, is_complete=True)
    
    # Access typed result
    print("\n" + "=" * 60)
    print("🎯 TYPED PYDANTIC RESULT:")
    print("=" * 60)
    print(f"  Response: {result.response[:100]}...")
    print(f"  Sentiment: {result.sentiment}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Requires Escalation: {result.requires_escalation}")
    if result.escalation_reason:
        print(f"  Escalation Reason: {result.escalation_reason}")
    if result.suggested_actions:
        print(f"  Suggested Actions ({len(result.suggested_actions)}):")
        for action in result.suggested_actions:
            print(f"    • {action}")


async def streaming_async_generator_example():
    """
    Example using async generator pattern.
    
    Yields incremental updates as fields arrive.
    """
    print("\n" + "=" * 60)
    print("STREAMING STRUCTURED OUTPUT DEMO (Async Generator)")
    print("=" * 60)
    
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="openai/gpt-4o-mini",
        temperature=0.7
    )
    
    query = "What is your return policy? I want to return an item I bought last week."
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    update_count = 0
    async for partial_response in agent.handle_inquiry_stream(
        customer_message=query,
        customer_id="customer_789",
        session_id="generator-session-101",
        tags=["support", "streaming"]
    ):
        update_count += 1
        print(f"\n--- Update #{update_count} ---")
        print(f"Response (so far): {partial_response.response[:80]}...")
        print(f"Sentiment: {partial_response.sentiment}")
        print(f"Confidence: {partial_response.confidence:.2f}")
        if partial_response.suggested_actions:
            print(f"Actions: {partial_response.suggested_actions}")
    
    print(f"\n✅ Streaming complete! Received {update_count} incremental updates")


async def streaming_with_early_stop_example():
    """
    Example showing how to stop streaming early based on conditions.
    
    Useful for:
    - Stopping when confidence is too low
    - Stopping when escalation is required
    - Stopping when certain fields are populated
    """
    print("\n" + "=" * 60)
    print("STREAMING WITH EARLY STOP")
    print("=" * 60)
    
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="openai/gpt-4o-mini",
        temperature=0.7
    )
    
    query = "I want to cancel my subscription immediately!"
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    async for partial_response in agent.handle_inquiry_stream(
        customer_message=query,
        customer_id="customer_early_stop",
        session_id="early-stop-session"
    ):
        # Stop early if escalation is required
        if partial_response.requires_escalation:
            print(f"\n⚠️  Early stop: Escalation required - {partial_response.escalation_reason}")
            break
        
        # Stop early if confidence is very low
        if partial_response.confidence < 0.3:
            print(f"\n⚠️  Early stop: Low confidence ({partial_response.confidence:.2f})")
            break
        
        print(f"Response progress: {len(partial_response.response)} chars, "
              f"Confidence: {partial_response.confidence:.2f}")


async def comparison_example():
    """
    Compare streaming vs non-streaming responses.
    
    Shows the difference in user experience:
    - Non-streaming: Wait for complete response
    - Streaming: See updates as they arrive
    """
    print("\n" + "=" * 60)
    print("COMPARISON: Streaming vs Non-Streaming")
    print("=" * 60)
    
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="openai/gpt-4o-mini",
        temperature=0.7
    )
    
    query = "Tell me about your products and services"
    
    print(f"\n🔍 Query: {query}\n")
    
    # Non-streaming (traditional)
    print("1️⃣  Non-streaming (waiting for complete response)...")
    import time
    start_time = time.time()
    response = await agent.handle_inquiry(
        customer_message=query,
        customer_id="customer_comparison"
    )
    non_streaming_time = time.time() - start_time
    print(f"   ✅ Received complete response in {non_streaming_time:.2f}s")
    print(f"   Response length: {len(response.response)} chars\n")
    
    # Streaming
    print("2️⃣  Streaming (receiving incremental updates)...")
    start_time = time.time()
    first_update_time = None
    update_count = 0
    
    async for partial_response in agent.handle_inquiry_stream(
        customer_message=query,
        customer_id="customer_comparison"
    ):
        if first_update_time is None:
            first_update_time = time.time() - start_time
            print(f"   ⚡ First update received in {first_update_time:.2f}s")
        update_count += 1
    
    streaming_time = time.time() - start_time
    print(f"   ✅ Streaming complete in {streaming_time:.2f}s")
    print(f"   Total updates: {update_count}")
    print(f"   Time to first update: {first_update_time:.2f}s")
    if first_update_time:
        print(f"   Perceived latency improvement: {non_streaming_time - first_update_time:.2f}s faster")


if __name__ == "__main__":
    # Run examples
    logger.info("🚀 Starting Streaming Structured Output Examples\n")
    
    # Example 1: Callback pattern (Agno-style)
    asyncio.run(streaming_with_callback_example())
    
    # Example 2: Async generator pattern
    asyncio.run(streaming_async_generator_example())
    
    # Example 3: Early stop
    asyncio.run(streaming_with_early_stop_example())
    
    # Example 4: Comparison
    asyncio.run(comparison_example())
