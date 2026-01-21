"""
Chat endpoints for LLM interactions with LangChain + OpenRouter.
"""

import uuid
from typing import Optional

from app.infrastructure.langfuse_handler import get_langfuse_config
from app.infrastructure.llm_provider import OpenRouterProvider
from app.security.clerk_auth import ClerkUser, require_current_user
from app.utils.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = get_logger("chat_api")

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, description="User message")
    model: Optional[str] = Field("openai/gpt-4o-mini", description="OpenRouter model name")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    session_id: Optional[str] = Field(None, description="Session ID for grouping related traces in Langfuse")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI response")
    model_used: str = Field(..., description="Model that was used")


@router.post("/", response_model=ChatResponse)
async def chat(
    request_body: ChatRequest,
    current_user: ClerkUser = Depends(require_current_user),
) -> ChatResponse:
    """
    Send a message to the LLM and get a response.
    
    Requires Clerk authentication. Uses LangChain with OpenRouter.
    No session storage - stateless conversation.
    """
    try:
        logger.info(f"Chat request from user {current_user.id}: {request_body.message[:50]}...")
        
        # Initialize OpenRouter provider
        provider = OpenRouterProvider()
        
        # Get LLM instance
        llm = provider.get_llm(
            model_name=request_body.model,
            temperature=request_body.temperature
        )
        
        # Create LangChain chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Provide clear, concise, and accurate responses."),
            ("user", "{input}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        # Build Langfuse config with filtering attributes for easy filtering in Langfuse
        # session_id groups related traces, user_id enables user-level filtering
        langfuse_config = get_langfuse_config(
            session_id=request_body.session_id or str(uuid.uuid4()),
            user_id=current_user.id,
            tags=["chat", "api"],
            metadata={
                "model": request_body.model,
                "temperature": request_body.temperature,
            },
        )
        
        # Invoke chain with Langfuse config
        response_text = await chain.ainvoke(
            {"input": request_body.message},
            config=langfuse_config
        )
        
        logger.info(f"Chat response generated successfully for user {current_user.id}")
        
        return ChatResponse(
            response=response_text,
            model_used=request_body.model
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process chat request")
