"""
Chat endpoints for {{cookiecutter.project_name}}.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_chat_service_dep,
    get_conversation_service_dep,
    validate_session_id,
    check_rate_limit
)
from app.core.security.clerk_auth import ClerkUser, get_current_user, require_current_user
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    ChatSession,
    MessageHistory
)
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user),
    _rate_limit_check = Depends(check_rate_limit)
) -> ChatResponse:
    """
    Send a message to the chat and get an AI response.
    
    This endpoint processes a user message through the LLM and returns
    an AI-generated response. It handles session management, caching,
    and event publishing automatically.
    """
    try:
        user_id = current_user.id if current_user else None
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
            context=request.context
        )
        return response
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(
    conversation_service: ConversationService = Depends(get_conversation_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
) -> List[ChatSession]:
    """
    List chat sessions.
    
    Returns a paginated list of chat sessions. If user_id is provided,
    only returns sessions for that user.
    """
    try:
        user_id = current_user.id if current_user else None
        sessions = await conversation_service.list_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return sessions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str = Depends(validate_session_id),
    conversation_service: ConversationService = Depends(get_conversation_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user)
) -> ChatSession:
    """
    Get a specific chat session with full message history.
    """
    try:
        user_id = current_user.id if current_user else None
        session = await conversation_service.get_session(
            session_id=session_id,
            user_id=user_id
        )
        
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        
        return session
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str = Depends(validate_session_id),
    conversation_service: ConversationService = Depends(get_conversation_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user)
) -> dict:
    """
    Delete a chat session and all its messages.
    """
    try:
        user_id = current_user.id if current_user else None
        success = await conversation_service.delete_session(
            session_id=session_id,
            user_id=user_id
        )
        
        if not success:
            raise NotFoundError(f"Session {session_id} not found")
        
        return {"message": f"Session {session_id} deleted successfully"}
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=MessageHistory)
async def get_session_messages(
    session_id: str = Depends(validate_session_id),
    conversation_service: ConversationService = Depends(get_conversation_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0
) -> MessageHistory:
    """
    Get paginated message history for a session.
    """
    try:
        user_id = current_user.id if current_user else None
        messages = await conversation_service.get_session_messages(
            session_id=session_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return MessageHistory(
            session_id=session_id,
            messages=messages,
            total=len(messages),
            limit=limit,
            offset=offset
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session messages: {str(e)}"
        )


@router.post("/sessions/{session_id}/clear")
async def clear_session(
    session_id: str = Depends(validate_session_id),
    conversation_service: ConversationService = Depends(get_conversation_service_dep),
    current_user: Optional[ClerkUser] = Depends(get_current_user)
) -> dict:
    """
    Clear all messages from a session while keeping the session.
    """
    try:
        user_id = current_user.id if current_user else None
        success = await conversation_service.clear_session_messages(
            session_id=session_id,
            user_id=user_id
        )
        
        if not success:
            raise NotFoundError(f"Session {session_id} not found")
        
        return {"message": f"Session {session_id} cleared successfully"}
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear session: {str(e)}"
        )
