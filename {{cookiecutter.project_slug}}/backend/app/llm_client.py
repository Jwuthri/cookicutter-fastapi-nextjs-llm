"""
LLM client for generating AI responses.
Supports multiple LLM providers based on cookiecutter configuration.
"""

import os
from typing import List, Optional
from .utils.logging import get_logger

logger = get_logger("llm_client")
from .models import ChatMessage
{% if cookiecutter.llm_provider == "openai" %}
import openai
{% elif cookiecutter.llm_provider == "anthropic" %}
import anthropic
{% elif cookiecutter.llm_provider == "huggingface" %}
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
{% endif %}


class LLMClient:
    """Client for interacting with LLM providers."""
    
    def __init__(self):
        self.provider = "{{cookiecutter.llm_provider}}"
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the LLM client based on the provider."""
        {% if cookiecutter.llm_provider == "openai" %}
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        {% elif cookiecutter.llm_provider == "anthropic" %}
        self.client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
        )
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        
        {% elif cookiecutter.llm_provider == "huggingface" %}
        model_name = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model.to(self.device)
            
            # Add pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            logger.error(f"Error loading HuggingFace model: {e}")
            raise
        {% endif %}
        
        logger.info(f"LLM client initialized with provider: {self.provider}")
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            message: The user's input message
            conversation_history: Previous messages in the conversation
            system_prompt: Optional system prompt to guide the AI's behavior
            
        Returns:
            The generated response string
        """
        try:
            {% if cookiecutter.llm_provider == "openai" %}
            return await self._generate_openai_response(message, conversation_history, system_prompt)
            {% elif cookiecutter.llm_provider == "anthropic" %}
            return await self._generate_anthropic_response(message, conversation_history, system_prompt)
            {% elif cookiecutter.llm_provider == "huggingface" %}
            return await self._generate_huggingface_response(message, conversation_history, system_prompt)
            {% else %}
            # Fallback for custom provider
            return f"Custom LLM response to: {message}"
            {% endif %}
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error while processing your message. Please try again."
    
    {% if cookiecutter.llm_provider == "openai" %}
    async def _generate_openai_response(
        self, 
        message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using OpenAI API."""
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."
            })
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    {% elif cookiecutter.llm_provider == "anthropic" %}
    async def _generate_anthropic_response(
        self, 
        message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using Anthropic API."""
        messages = []
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        system_message = system_prompt or "You are a helpful AI assistant. Provide clear, concise, and helpful responses."
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_message,
            messages=messages
        )
        
        return response.content[0].text
    
    {% elif cookiecutter.llm_provider == "huggingface" %}
    async def _generate_huggingface_response(
        self, 
        message: str, 
        conversation_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using HuggingFace model."""
        # Build conversation context
        context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages to avoid token limit
                context += f"{msg.role}: {msg.content}\n"
        
        # Add current message
        context += f"user: {message}\nassistant:"
        
        # Encode and generate
        inputs = self.tokenizer.encode(context, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 100,
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.9
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new part of the response
        response = response[len(context):].strip()
        
        return response if response else "I'm sorry, I couldn't generate a proper response. Please try again."
    {% endif %}
    
    def get_provider_info(self) -> dict:
        """Get information about the current LLM provider."""
        return {
            "provider": self.provider,
            {% if cookiecutter.llm_provider == "openai" %}
            "model": self.model,
            "api_configured": bool(os.getenv("OPENAI_API_KEY"))
            {% elif cookiecutter.llm_provider == "anthropic" %}
            "model": self.model,
            "api_configured": bool(os.getenv("ANTHROPIC_API_KEY"))
            {% elif cookiecutter.llm_provider == "huggingface" %}
            "model": os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium"),
            "device": getattr(self, 'device', 'cpu'),
            "local_model": True
            {% else %}
            "model": "custom",
            "api_configured": True
            {% endif %}
        }
