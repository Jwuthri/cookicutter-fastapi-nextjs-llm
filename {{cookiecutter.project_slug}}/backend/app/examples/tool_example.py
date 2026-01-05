"""
Example use case: Using LangChain tools with agents.

This example demonstrates:
1. Creating and using LangChain tools
2. Binding tools to an LLM
3. Using tools in agent workflows
"""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from app.agents.tool.context_manager import (
    summarize_history,
    count_history_items,
    get_recent_items,
    estimate_tokens,
    format_history_for_display,
    CONTEXT_MANAGER_TOOLS,
)
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.logging import get_logger

logger = get_logger("tool_example")


def basic_tool_usage():
    """Example of using tools directly."""
    logger.info("=== Basic Tool Usage ===")
    
    # Example history
    history = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language..."},
    ]
    
    # Use count_history_items tool
    count = count_history_items.invoke({"history": history})
    logger.info(f"History has {count} items")
    
    # Use get_recent_items tool
    recent = get_recent_items.invoke({"history": history, "n": 2})
    logger.info(f"Recent items: {len(recent)}")
    
    # Use format_history_for_display tool
    formatted = format_history_for_display.invoke({"history": history})
    logger.info(f"Formatted history:\n{formatted}")
    
    # Use estimate_tokens tool
    text = "Hello, this is a test message."
    tokens = estimate_tokens.invoke({"text": text})
    logger.info(f"Estimated tokens for '{text}': {tokens}")


def tool_with_llm():
    """Example of binding tools to an LLM."""
    logger.info("\n=== Tool with LLM ===")
    
    # Initialize provider
    provider = OpenRouterProvider()
    llm = provider.get_llm(model_name="openai/gpt-4o-mini", temperature=0)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(CONTEXT_MANAGER_TOOLS)
    
    # Create a prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with access to context management tools."),
        ("user", "{input}")
    ])
    
    # Create chain
    chain = prompt | llm_with_tools
    
    # Invoke with a request that might use tools
    response = chain.invoke({
        "input": "I have a conversation history with 50 items. How many items are there?"
    })
    
    logger.info(f"Response: {response}")
    
    # Check if the LLM wants to use tools
    if hasattr(response, 'tool_calls') and response.tool_calls:
        logger.info(f"LLM wants to use {len(response.tool_calls)} tool(s)")
        for tool_call in response.tool_calls:
            logger.info(f"Tool: {tool_call.get('name')}")
            logger.info(f"Args: {tool_call.get('args')}")


def tool_workflow_example():
    """Example of a workflow using multiple tools."""
    logger.info("\n=== Tool Workflow Example ===")
    
    # Example history
    history = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(25)  # 25 items
    ]
    
    # Step 1: Count items
    item_count = count_history_items.invoke({"history": history})
    logger.info(f"Step 1: History has {item_count} items")
    
    # Step 2: Get recent items if too many
    if item_count > 10:
        recent = get_recent_items.invoke({"history": history, "n": 10})
        logger.info(f"Step 2: Keeping {len(recent)} recent items")
        
        # Step 3: Format for display
        formatted = format_history_for_display.invoke({"history": recent})
        logger.info(f"Step 3: Formatted history:\n{formatted}")
        
        # Step 4: Estimate tokens
        history_text = str(recent)
        tokens = estimate_tokens.invoke({"text": history_text})
        logger.info(f"Step 4: Estimated tokens: {tokens}")


def custom_tool_example():
    """Example of creating a custom tool."""
    logger.info("\n=== Custom Tool Example ===")
    
    from langchain_core.tools import tool
    
    @tool
    def calculate_context_usage(
        system_prompt: str,
        history: str,
        current_message: str
    ) -> dict:
        """
        Calculate context usage breakdown.
        
        Args:
            system_prompt: System prompt text
            history: Conversation history text
            current_message: Current message text
        
        Returns:
            Dictionary with token estimates for each component
        """
        return {
            "system_prompt_tokens": len(system_prompt) // 4,
            "history_tokens": len(history) // 4,
            "current_message_tokens": len(current_message) // 4,
            "total_tokens": (len(system_prompt) + len(history) + len(current_message)) // 4
        }
    
    # Use the custom tool
    result = calculate_context_usage.invoke({
        "system_prompt": "You are a helpful assistant.",
        "history": "User: Hello\nAssistant: Hi there!",
        "current_message": "What is 2+2?"
    })
    
    logger.info(f"Context usage: {result}")


if __name__ == "__main__":
    basic_tool_usage()
    tool_with_llm()
    tool_workflow_example()
    custom_tool_example()
