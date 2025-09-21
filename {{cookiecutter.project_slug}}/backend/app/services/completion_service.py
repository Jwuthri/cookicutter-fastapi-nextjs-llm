"""
Completion service for {{cookiecutter.project_name}}.
"""

from typing import Optional, AsyncGenerator

from app.core.llm.base import BaseLLMClient
from app.models.completion import CompletionRequest
from app.exceptions import ValidationError, LLMError
from loguru import logger


class CompletionService:
    """Service for handling text completions."""
    
    def __init__(self, llm_service: BaseLLMClient):
        self.llm = llm_service
    
    async def generate_completion(self, request: CompletionRequest) -> str:
        """Generate a text completion."""
        try:
            # Validate request
            if not request.prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            
            # Generate completion
            completion = await self.llm.generate_completion(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop_sequences=request.stop,
                system_message=request.system_message
            )
            
            return completion
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise LLMError(f"Failed to generate completion: {str(e)}")
    
    async def generate_streaming_completion(
        self, 
        request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming text completion."""
        try:
            # Validate request
            if not request.prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            
            # Generate streaming completion
            async for chunk in self.llm.generate_streaming_completion(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop_sequences=request.stop,
                system_message=request.system_message
            ):
                yield chunk
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error generating streaming completion: {e}")
            raise LLMError(f"Failed to generate streaming completion: {str(e)}")
