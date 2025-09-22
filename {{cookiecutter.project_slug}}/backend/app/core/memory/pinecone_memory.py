"""
Pinecone vector database memory implementation for {{cookiecutter.project_name}}.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import hashlib

from app.core.memory.base import MemoryInterface
from app.models.chat import ChatMessage, ChatSession
from app.exceptions import DatabaseError
from ...utils.logging import get_logger

logger = get_logger("pinecone_memory")

try:
    import pinecone
    from pinecone import Pinecone
except ImportError:
    pinecone = None
    Pinecone = None

try:
    from openai import OpenAI
    import numpy as np
except ImportError:
    OpenAI = None
    np = None


class PineconeMemory(MemoryInterface):
    """Pinecone-based vector memory storage implementation."""
    
    def __init__(self, api_key: str, environment: str = "gcp-starter", index_name: str = "chat-memory"):
        if Pinecone is None:
            raise ImportError("Pinecone package not installed. Install with: uv add pinecone-client")
        
        if OpenAI is None:
            raise ImportError("OpenAI package not installed for embeddings. Install with: uv add openai")
            
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = 1536  # OpenAI text-embedding-ada-002 dimension
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Initialize OpenAI for embeddings
        self.openai_client = OpenAI()
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Get index
        self.index = self.pc.Index(self.index_name)
        
        logger.info(f"Pinecone memory initialized with index: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists."""
        try:
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise DatabaseError(f"Failed to create Pinecone index: {str(e)}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise DatabaseError(f"Failed to generate embedding: {str(e)}")
    
    def _create_vector_id(self, session_id: str, message_id: str) -> str:
        """Create a unique vector ID."""
        return f"{session_id}_{message_id}"
    
    def _create_session_id(self, session_id: str) -> str:
        """Create session metadata ID."""
        return f"session_{session_id}"
    
    async def store_session(
        self, 
        session_id: str, 
        messages: List[ChatMessage],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Store a chat session in Pinecone."""
        try:
            vectors_to_upsert = []
            
            # Store session metadata
            session_vector_id = self._create_session_id(session_id)
            session_text = f"Session: {session_id}"
            if metadata:
                session_text += f" Metadata: {json.dumps(metadata)}"
            
            session_embedding = self._generate_embedding(session_text)
            
            vectors_to_upsert.append({
                "id": session_vector_id,
                "values": session_embedding,
                "metadata": {
                    "type": "session",
                    "session_id": session_id,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "message_count": len(messages),
                    "session_metadata": json.dumps(metadata or {})
                }
            })
            
            # Store individual messages as vectors
            for msg in messages:
                vector_id = self._create_vector_id(session_id, msg.id)
                embedding = self._generate_embedding(msg.content)
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "type": "message",
                        "session_id": session_id,
                        "message_id": msg.id,
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "user_id": user_id,
                        "message_metadata": json.dumps(msg.metadata or {})
                    }
                })
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing session in Pinecone: {e}")
            raise DatabaseError(f"Failed to store session: {str(e)}")
    
    async def get_session(
        self, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[ChatSession]:
        """Retrieve a chat session from Pinecone."""
        try:
            # Query for session metadata
            session_filter = {
                "type": "session",
                "session_id": session_id
            }
            if user_id:
                session_filter["user_id"] = user_id
            
            session_results = self.index.query(
                vector=[0.0] * self.dimension,  # Dummy vector for metadata query
                filter=session_filter,
                top_k=1,
                include_metadata=True
            )
            
            if not session_results.matches:
                return None
            
            session_match = session_results.matches[0]
            session_metadata = session_match.metadata
            
            # Query for all messages in the session
            message_filter = {
                "type": "message",
                "session_id": session_id
            }
            if user_id:
                message_filter["user_id"] = user_id
            
            message_results = self.index.query(
                vector=[0.0] * self.dimension,  # Dummy vector for metadata query
                filter=message_filter,
                top_k=1000,  # Retrieve all messages
                include_metadata=True
            )
            
            # Convert to ChatMessage objects
            messages = []
            for match in message_results.matches:
                msg_meta = match.metadata
                messages.append(ChatMessage(
                    id=msg_meta["message_id"],
                    content=msg_meta["content"],
                    role=msg_meta["role"],
                    timestamp=msg_meta["timestamp"],
                    metadata=json.loads(msg_meta.get("message_metadata", "{}"))
                ))
            
            # Sort messages by timestamp
            messages.sort(key=lambda x: x.timestamp)
            
            return ChatSession(
                session_id=session_id,
                messages=messages,
                created_at=session_metadata.get("created_at"),
                updated_at=datetime.now().isoformat(),
                metadata=json.loads(session_metadata.get("session_metadata", "{}"))
            )
            
        except Exception as e:
            logger.error(f"Error getting session from Pinecone: {e}")
            raise DatabaseError(f"Failed to get session: {str(e)}")
    
    async def delete_session(
        self, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a chat session from Pinecone."""
        try:
            # Get all vector IDs for this session
            session_filter = {
                "session_id": session_id
            }
            if user_id:
                session_filter["user_id"] = user_id
            
            results = self.index.query(
                vector=[0.0] * self.dimension,
                filter=session_filter,
                top_k=10000,  # Get all vectors for this session
                include_metadata=True
            )
            
            if not results.matches:
                return False
            
            # Delete all vectors for this session
            vector_ids = [match.id for match in results.matches]
            self.index.delete(ids=vector_ids)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session from Pinecone: {e}")
            raise DatabaseError(f"Failed to delete session: {str(e)}")
    
    async def list_sessions(
        self, 
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """List chat sessions from Pinecone."""
        try:
            session_filter = {"type": "session"}
            if user_id:
                session_filter["user_id"] = user_id
            
            results = self.index.query(
                vector=[0.0] * self.dimension,
                filter=session_filter,
                top_k=1000,  # Pinecone limit
                include_metadata=True
            )
            
            sessions = []
            for match in results.matches:
                metadata = match.metadata
                session_id = metadata["session_id"]
                
                # Get basic session info without all messages for efficiency
                session = ChatSession(
                    session_id=session_id,
                    messages=[],  # Don't load messages for list view
                    created_at=metadata.get("created_at"),
                    updated_at=datetime.now().isoformat(),
                    metadata={
                        "message_count": metadata.get("message_count", 0),
                        **json.loads(metadata.get("session_metadata", "{}"))
                    }
                )
                sessions.append(session)
            
            # Apply manual pagination (Pinecone doesn't have native pagination)
            return sessions[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error listing sessions from Pinecone: {e}")
            return []
    
    async def add_message(
        self, 
        session_id: str, 
        message: ChatMessage,
        user_id: Optional[str] = None
    ) -> bool:
        """Add a message to an existing session."""
        try:
            vector_id = self._create_vector_id(session_id, message.id)
            embedding = self._generate_embedding(message.content)
            
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "type": "message",
                    "session_id": session_id,
                    "message_id": message.id,
                    "role": message.role.value,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "user_id": user_id,
                    "message_metadata": json.dumps(message.metadata or {})
                }
            }
            
            self.index.upsert(vectors=[vector])
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to Pinecone: {e}")
            raise DatabaseError(f"Failed to add message: {str(e)}")
    
    async def get_messages(
        self, 
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[ChatMessage]:
        """Get messages from a session."""
        session = await self.get_session(session_id, user_id)
        if not session:
            return []
        
        return session.messages[offset:offset + limit]
    
    async def clear_session_messages(
        self, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Clear all messages from a session."""
        try:
            # Delete only message vectors, keep session metadata
            message_filter = {
                "type": "message",
                "session_id": session_id
            }
            if user_id:
                message_filter["user_id"] = user_id
            
            results = self.index.query(
                vector=[0.0] * self.dimension,
                filter=message_filter,
                top_k=10000,
                include_metadata=True
            )
            
            if results.matches:
                vector_ids = [match.id for match in results.matches]
                self.index.delete(ids=vector_ids)
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session messages from Pinecone: {e}")
            raise DatabaseError(f"Failed to clear session messages: {str(e)}")
    
    async def update_session_metadata(
        self, 
        session_id: str, 
        metadata: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """Update session metadata."""
        try:
            session = await self.get_session(session_id, user_id)
            if not session:
                return False
            
            # Update session metadata
            session.metadata.update(metadata)
            
            # Re-store session with updated metadata
            return await self.store_session(session_id, session.messages, session.metadata, user_id)
            
        except Exception as e:
            logger.error(f"Error updating session metadata in Pinecone: {e}")
            raise DatabaseError(f"Failed to update session metadata: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Pinecone health."""
        try:
            # Simple query to test connection
            self.index.query(
                vector=[0.0] * self.dimension,
                top_k=1
            )
            return True
        except Exception:
            return False
    
    async def semantic_search(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on chat messages."""
        try:
            query_embedding = self._generate_embedding(query)
            
            search_filter = {"type": "message"}
            if session_id:
                search_filter["session_id"] = session_id
            
            results = self.index.query(
                vector=query_embedding,
                filter=search_filter,
                top_k=limit,
                include_metadata=True
            )
            
            search_results = []
            for match in results.matches:
                metadata = match.metadata
                search_results.append({
                    "content": metadata["content"],
                    "role": metadata["role"],
                    "session_id": metadata["session_id"],
                    "timestamp": metadata["timestamp"],
                    "score": match.score
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []
