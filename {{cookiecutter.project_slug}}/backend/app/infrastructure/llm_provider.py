"""LLM provider integrations using LangChain."""
from typing import Any, Dict, List, Optional

import requests
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("llm_provider")


class OpenRouterProvider:
    """OpenRouter LLM provider integration with model querying capabilities."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY from settings)
        """
        settings = get_settings()
        self.api_key = api_key or settings.openrouter_api_key
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. Please set the OPENROUTER_API_KEY environment variable."
            )
        self._base_url = "https://openrouter.ai/api/v1"
        self._models_cache: Optional[List[Dict[str, Any]]] = None
    
    def get_llm(
        self,
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0,
        callbacks: Optional[List] = None,
    ) -> ChatOpenAI:
        """
        Get configured OpenRouter LLM instance.
        
        Args:
            model_name: OpenRouter model name (e.g., "openai/gpt-4o-mini")
            temperature: Model temperature (0-2)
            callbacks: Optional list of callback handlers
        
        Returns:
            Configured ChatOpenAI instance for OpenRouter
        """
        return ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            base_url=f"{self._base_url}",
            temperature=temperature,
            callbacks=callbacks,
        )
    
    def get_models(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.
        
        Args:
            use_cache: Whether to use cached models if available
        
        Returns:
            List of model dictionaries with id, context_length, pricing, etc.
        
        Raises:
            requests.RequestException: If the API request fails
        """
        if use_cache and self._models_cache is not None:
            return self._models_cache
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(
                f"{self._base_url}/models",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            models = response.json().get("data", [])
            logger.info(f"Fetched {len(models)} available models from OpenRouter")
            self._models_cache = models
            return models
        except requests.RequestException as e:
            logger.error(f"Failed to fetch OpenRouter models: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get OpenRouter account balance/credits.
        
        Returns:
            Dictionary with balance information
        
        Raises:
            requests.RequestException: If the API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(
                f"{self._base_url}/auth/key",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            balance = response.json()
            logger.info(f"OpenRouter balance: ${balance.get('balance', 0):.2f}")
            return balance
        except requests.RequestException as e:
            logger.error(f"Failed to fetch OpenRouter balance: {e}")
            raise
    
    @staticmethod
    def get_provider_from_id(model_id: str) -> Optional[str]:
        """Extract provider name from model ID (e.g., 'openai/gpt-4' -> 'openai')."""
        if "/" in model_id:
            return model_id.split("/")[0]
        return None
    
    def get_model_context_limit(
        self,
        model_name: str,
        use_cache: bool = True
    ) -> Optional[int]:
        """
        Get model context limit from OpenRouter models cache.
        
        Args:
            model_name: Model name (e.g., "openai/gpt-4o-mini")
            use_cache: Whether to use cached models
        
        Returns:
            Context limit if found, None otherwise
        """
        try:
            models = self.get_models(use_cache=use_cache)
            for model in models:
                if model.get('id') == model_name:
                    top_provider = model.get('top_provider', {})
                    if isinstance(top_provider, dict):
                        context_length = top_provider.get('context_length')
                        if context_length:
                            return int(context_length)
            logger.warning(f"Model {model_name} not found in OpenRouter models")
            return None
        except Exception as e:
            logger.error(f"Failed to get model context limit: {e}")
            return None
    
    def get_model_max_completion(
        self,
        model_name: str,
        use_cache: bool = True
    ) -> Optional[int]:
        """
        Get model max completion tokens from OpenRouter models cache.
        
        Args:
            model_name: Model name (e.g., "openai/gpt-4o-mini")
            use_cache: Whether to use cached models
        
        Returns:
            Max completion tokens if found, None otherwise
        """
        try:
            models = self.get_models(use_cache=use_cache)
            for model in models:
                if model.get('id') == model_name:
                    top_provider = model.get('top_provider', {})
                    if isinstance(top_provider, dict):
                        max_completion = top_provider.get('max_completion_tokens')
                        if max_completion:
                            return int(max_completion)
            logger.warning(f"Model {model_name} not found in OpenRouter models")
            return None
        except Exception as e:
            logger.error(f"Failed to get model max completion: {e}")
            return None
