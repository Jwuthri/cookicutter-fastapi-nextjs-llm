"""
Chat session model for {{cookiecutter.project_name}}.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..base import Base


class ChatSession(Base):
    """Chat session model for storing conversations."""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Allow anonymous sessions
    
    # Session metadata
    title = Column(String(500), nullable=True)  # Auto-generated or user-set title
    system_prompt = Column(Text, nullable=True)  # Custom system prompt for this session
    model_name = Column(String(100), nullable=True)  # LLM model used
    
    # Session state
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, nullable=True)
    
    # Session settings and metadata
    settings = Column(JSON, default={})  # Temperature, max_tokens, etc.
    metadata = Column(JSON, default={})  # Additional session data
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_chat_sessions_user_created', 'user_id', 'created_at'),
        Index('idx_chat_sessions_active', 'is_active', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"
