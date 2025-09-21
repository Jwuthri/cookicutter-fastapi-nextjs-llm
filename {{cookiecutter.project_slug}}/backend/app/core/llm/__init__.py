"""
Agno + OpenRouter LLM clients for {{cookiecutter.project_name}}.
Unified access to 500+ models through Agno's powerful agent framework.
"""

from .factory import get_llm_client, list_available_providers, validate_provider_config
from .openrouter_client import AgnoOpenRouterClient
