# Agents Structure

This directory contains the agent implementations following a modular structure pattern.

## Directory Structure

```
agents/
├── __init__.py                 # Main exports
├── agents/                     # Agent implementations
│   ├── __init__.py
│   └── context_manager.py      # Context management agent
├── prompt/                      # Prompt templates
│   ├── __init__.py
│   └── context_manager.py      # Prompts for context manager
├── tool/                        # LangChain tools
│   ├── __init__.py
│   └── context_manager.py      # Tools for context manager
└── structured_output/           # Pydantic models for structured outputs
    ├── __init__.py
    └── context_manager.py       # Output models for context manager
```

## Pattern

Each agent follows this structure:

1. **Agent Implementation** (`agents/`): The main agent class with business logic
2. **Prompts** (`prompt/`): System prompts and user message templates
3. **Tools** (`tool/`): LangChain tools that the agent can use
4. **Structured Outputs** (`structured_output/`): Pydantic models for type-safe outputs

## Adding a New Agent

To add a new agent (e.g., `evaluation`):

1. Create `agents/evaluation.py` with your agent class
2. Create `prompt/evaluation.py` with prompt templates
3. Create `tool/evaluation.py` with any tools needed
4. Create `structured_output/evaluation.py` with output models
5. Update `__init__.py` files to export your new agent

## Example Usage

### Using the Agent

```python
from app.agents.agents.context_manager import ContextManagerAgent, ContextCheckRequest
from app.infrastructure.llm_provider import OpenRouterProvider

# Initialize
provider = OpenRouterProvider()
agent = ContextManagerAgent(provider, model_name="openai/gpt-4o-mini")

# Check context
request = ContextCheckRequest(
    system_prompt="You are a helpful assistant.",
    history=[...],
    current_item="New message",
    model_name="openai/gpt-4o-mini"
)

result = agent.check_context(request)
```

### Using Tools

```python
from app.agents.tool.context_manager import (
    count_history_items,
    get_recent_items,
    format_history_for_display,
    CONTEXT_MANAGER_TOOLS
)
from app.infrastructure.llm_provider import OpenRouterProvider

# Use tools directly
history = [{"role": "user", "content": "Hello"}]
count = count_history_items.invoke({"history": history})

# Bind tools to LLM
provider = OpenRouterProvider()
llm = provider.get_llm(model_name="openai/gpt-4o-mini")
llm_with_tools = llm.bind_tools(CONTEXT_MANAGER_TOOLS)

# LLM can now use these tools when needed
response = llm_with_tools.invoke("Count the items in my history")
```

### Creating Custom Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input_text: str) -> str:
    """Description of what the tool does."""
    # Tool implementation
    return processed_result

# Use the tool
result = my_custom_tool.invoke({"input_text": "example"})
```
