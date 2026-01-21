"""
Full example: Streaming structured output with LangChain + OpenRouter.

Shows the structured object being built incrementally during streaming,
similar to Agno's approach. Demonstrates both async generator and callback patterns.
"""

import asyncio
import json
import time
from typing import Callable, Optional

from app.agents.agents import CustomerSupportAgent
from app.agents.structured_output.customer_support import CustomerSupportResponse
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger

logger = get_logger("streaming_structured_output_example")


async def streaming_with_callback_example():
    """
    Example using callback pattern (Agno-style).
    
    Shows incremental updates as the structured object is being built.
    """
    print("=" * 60)
    print("STREAMING STRUCTURED OUTPUT DEMO (Callback Pattern)")
    print("=" * 60)
    
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="anthropic/claude-4.5-sonnet",
        temperature=0.1
    )
    
    query = (
        "I need help with my order #12345. It hasn't arrived yet and I'm very frustrated! "
        "This is the third time this has happened. I want a refund and to speak to a manager."
    )
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    update_count = 0
    start_time = time.time()
    
    def stream_callback(response: CustomerSupportResponse):
        """Callback function called on each incremental update."""
        nonlocal update_count
        update_count += 1
        elapsed = time.time() - start_time
        # Show progress inline
        print(f"[{elapsed:.2f}s] Update #{update_count}: "
              f"response={len(response.response)} chars, "
              f"sentiment={response.sentiment}, "
              f"confidence={response.confidence:.2f}, "
              f"actions={len(response.suggested_actions)}")
    
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
    print("\n" + "=" * 60)
    print("✅ FINAL STRUCTURED OUTPUT:")
    print("=" * 60)
    print(json.dumps(result.model_dump(), indent=2))
    
    print(f"\n📊 Total updates received: {update_count}")


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
        model_name="anthropic/claude-4.5-sonnet",
        temperature=0.1
    )
    
    query = "What is your return policy? I want to return an item I bought last week."
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    update_count = 0
    start_time = time.time()
    last_response: Optional[CustomerSupportResponse] = None
    
    async for partial_response in agent.handle_inquiry_stream(
        customer_message=query,
        customer_id="customer_789",
        session_id="generator-session-101",
        tags=["support", "streaming"]
    ):
        update_count += 1
        elapsed = time.time() - start_time
        last_response = partial_response
        
        # Show progress - only print every 5th update to avoid spam
        if update_count <= 5 or update_count % 5 == 0:
            print(f"[{elapsed:.2f}s] Update #{update_count}: "
                  f"response={len(partial_response.response)} chars, "
                  f"sentiment={partial_response.sentiment}")
    
    print(f"\n✅ Streaming complete! Received {update_count} incremental updates")
    
    if last_response:
        print(f"\n📝 Final response preview: {last_response.response[:100]}...")


async def streaming_with_early_stop_example():
    """
    Example showing how to stop streaming early based on conditions.
    
    Useful for:
    - Stopping when escalation is required
    - Stopping when certain fields are populated
    - Stopping when you have enough content
    """
    print("\n" + "=" * 60)
    print("STREAMING WITH EARLY STOP")
    print("=" * 60)
    
    provider = OpenRouterProvider()
    agent = CustomerSupportAgent(
        llm_provider=provider,
        model_name="anthropic/claude-4.5-sonnet",
        temperature=0.1
    )
    
    query = "I want to cancel my subscription immediately!"
    
    print(f"\n🔍 Customer Query: {query}\n")
    
    update_count = 0
    start_time = time.time()
    
    async for partial_response in agent.handle_inquiry_stream(
        customer_message=query,
        customer_id="customer_early_stop",
        session_id="early-stop-session"
    ):
        update_count += 1
        elapsed = time.time() - start_time
        
        print(f"[{elapsed:.2f}s] Update #{update_count}: "
              f"response={len(partial_response.response)} chars")
        
        # Stop early if escalation is required
        if partial_response.requires_escalation and partial_response.escalation_reason:
            print(f"\n⚠️  Early stop: Escalation required!")
            print(f"   Reason: {partial_response.escalation_reason}")
            break
        
        # Stop early if we have enough response content (e.g., for preview)
        if len(partial_response.response) > 150:
            print(f"\n⚠️  Early stop: Got enough content for preview!")
            print(f"   Preview: {partial_response.response[:100]}...")
            break


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
        model_name="anthropic/claude-4.5-sonnet",
        temperature=0.1
    )
    
    query = "Tell me about your products and services"
    
    print(f"\n🔍 Query: {query}\n")
    
    # Non-streaming (traditional)
    print("1️⃣  Non-streaming (waiting for complete response)...")
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
        improvement = non_streaming_time - first_update_time
        print(f"   Perceived latency improvement: {improvement:.2f}s faster")


async def main():
    """Run all examples."""
    logger.info("🚀 Starting Streaming Structured Output Examples\n")
    
    # Example 1: Callback pattern (Agno-style)
    await streaming_with_callback_example()
    
    # Example 2: Async generator pattern
    await streaming_async_generator_example()
    
    # Example 3: Early stop
    await streaming_with_early_stop_example()
    
    # Example 4: Comparison
    await comparison_example()


if __name__ == "__main__":
    asyncio.run(main())
