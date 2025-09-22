"""
Weaviate vector database memory implementation for {{cookiecutter.project_name}}.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid as uuid_lib

from app.core.memory.base import MemoryInterface
from app.models.chat import ChatMessage, ChatSession
from app.exceptions import DatabaseError
from ...utils.logging import get_logger

logger = get_logger("weaviate_memory")

try:
    import weaviate
    from weaviate.client import Client
except ImportError:
    weaviate = None
    Client = None


class WeaviateMemory(MemoryInterface):
    """Weaviate-based vector memory storage implementation."""
    
    def __init__(
        self, 
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        if weaviate is None:
            raise ImportError("Weaviate package not installed. Install with: uv add weaviate-client")
            
        self.url = url
        self.api_key = api_key
        self.openai_api_key = openai_api_key
        
        # Configure authentication
        auth_config = None
        if api_key:
            auth_config = weaviate.AuthApiKey(api_key=api_key)
        
        # Configure additional headers for OpenAI
        additional_headers = {}
        if openai_api_key:
            additional_headers["X-OpenAI-Api-Key"] = openai_api_key
        
        # Initialize Weaviate client
        self.client = weaviate.Client(
            url=url,
            auth_client_secret=auth_config,
            additional_headers=additional_headers
        )
        
        # Define class schemas
        self.session_class = "ChatSession"
        self.message_class = "ChatMessage"
        
        # Create schemas if they don't exist
        self._ensure_schemas_exist()
        
        logger.info(f"Weaviate memory initialized at: {url}")
    
    def _ensure_schemas_exist(self):
        """Ensure the required Weaviate schemas exist."""
        try:
            existing_classes = self.client.schema.get()["classes"]
            existing_class_names = [cls["class"] for cls in existing_classes]
            
            # Create ChatSession class if it doesn't exist
            if self.session_class not in existing_class_names:
                session_schema = {
                    "class": self.session_class,
                    "description": "Chat session metadata",
                    "vectorizer": "text2vec-openai",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada",
                            "modelVersion": "002",
                            "type": "text"
                        }
                    },
                    "properties": [
                        {
                            "name": "sessionId",
                            "dataType": ["string"],
                            "description": "Unique session identifier"
                        },
                        {
                            "name": "userId",
                            "dataType": ["string"],
                            "description": "User identifier"
                        },
                        {
                            "name": "createdAt",
                            "dataType": ["date"],
                            "description": "Session creation timestamp"
                        },
                        {
                            "name": "updatedAt", 
                            "dataType": ["date"],
                            "description": "Session update timestamp"
                        },
                        {
                            "name": "messageCount",
                            "dataType": ["int"],
                            "description": "Number of messages in session"
                        },
                        {
                            "name": "metadata",
                            "dataType": ["text"],
                            "description": "Session metadata as JSON"
                        },
                        {
                            "name": "summary",
                            "dataType": ["text"],
                            "description": "Session summary for vector search"
                        }
                    ]
                }
                self.client.schema.create_class(session_schema)
                logger.info(f"Created Weaviate class: {self.session_class}")
            
            # Create ChatMessage class if it doesn't exist
            if self.message_class not in existing_class_names:
                message_schema = {
                    "class": self.message_class,
                    "description": "Individual chat messages",
                    "vectorizer": "text2vec-openai",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada",
                            "modelVersion": "002",
                            "type": "text"
                        }
                    },
                    "properties": [
                        {
                            "name": "sessionId",
                            "dataType": ["string"],
                            "description": "Session this message belongs to"
                        },
                        {
                            "name": "messageId",
                            "dataType": ["string"],
                            "description": "Unique message identifier"
                        },
                        {
                            "name": "role",
                            "dataType": ["string"],
                            "description": "Message role (user/assistant/system)"
                        },
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "Message content"
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["date"],
                            "description": "Message timestamp"
                        },
                        {
                            "name": "userId",
                            "dataType": ["string"],
                            "description": "User identifier"
                        },
                        {
                            "name": "messageMetadata",
                            "dataType": ["text"],
                            "description": "Message metadata as JSON"
                        }
                    ]
                }
                self.client.schema.create_class(message_schema)
                logger.info(f"Created Weaviate class: {self.message_class}")
                
        except Exception as e:
            logger.error(f"Error ensuring Weaviate schemas exist: {e}")
            raise DatabaseError(f"Failed to create Weaviate schemas: {str(e)}")
    
    def _generate_uuid(self, text: str) -> str:
        """Generate a deterministic UUID from text."""
        return str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, text))
    
    async def store_session(
        self, 
        session_id: str, 
        messages: List[ChatMessage],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Store a chat session in Weaviate."""
        try:
            # Create session summary for vector search
            summary_parts = []
            for msg in messages[-5:]:  # Last 5 messages for summary
                summary_parts.append(f"{msg.role}: {msg.content[:100]}")
            session_summary = " | ".join(summary_parts)
            
            # Store session metadata
            session_uuid = self._generate_uuid(f"session_{session_id}")
            session_data = {
                "sessionId": session_id,
                "userId": user_id,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "messageCount": len(messages),
                "metadata": json.dumps(metadata or {}),
                "summary": session_summary
            }
            
            self.client.data_object.create(
                data_object=session_data,
                class_name=self.session_class,
                uuid=session_uuid
            )
            
            # Store individual messages
            for msg in messages:
                message_uuid = self._generate_uuid(f"message_{session_id}_{msg.id}")
                message_data = {
                    "sessionId": session_id,
                    "messageId": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "userId": user_id,
                    "messageMetadata": json.dumps(msg.metadata or {})
                }
                
                self.client.data_object.create(
                    data_object=message_data,
                    class_name=self.message_class,
                    uuid=message_uuid
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing session in Weaviate: {e}")
            raise DatabaseError(f"Failed to store session: {str(e)}")
    
    async def get_session(
        self, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[ChatSession]:
        """Retrieve a chat session from Weaviate."""
        try:
            # Get session metadata
            where_filter = {
                "path": ["sessionId"],
                "operator": "Equal",
                "valueString": session_id
            }
            
            if user_id:
                where_filter = {
                    "operator": "And",
                    "operands": [
                        where_filter,
                        {
                            "path": ["userId"],
                            "operator": "Equal", 
                            "valueString": user_id
                        }
                    ]
                }
            
            session_result = self.client.query.get(self.session_class, [
                "sessionId", "userId", "createdAt", "updatedAt", "messageCount", "metadata"
            ]).with_where(where_filter).with_limit(1).do()
            
            if not session_result["data"]["Get"][self.session_class]:
                return None
            
            session_data = session_result["data"]["Get"][self.session_class][0]
            
            # Get all messages for this session
            message_where = {
                "path": ["sessionId"],
                "operator": "Equal",
                "valueString": session_id
            }
            
            if user_id:
                message_where = {
                    "operator": "And",
                    "operands": [
                        message_where,
                        {
                            "path": ["userId"],
                            "operator": "Equal",
                            "valueString": user_id
                        }
                    ]
                }
            
            message_result = self.client.query.get(self.message_class, [
                "messageId", "role", "content", "timestamp", "messageMetadata"
            ]).with_where(message_where).with_limit(1000).do()
            
            # Convert to ChatMessage objects
            messages = []
            for msg_data in message_result["data"]["Get"][self.message_class]:
                messages.append(ChatMessage(
                    id=msg_data["messageId"],
                    content=msg_data["content"],
                    role=msg_data["role"],
                    timestamp=msg_data["timestamp"],
                    metadata=json.loads(msg_data.get("messageMetadata", "{}"))
                ))
            
            # Sort messages by timestamp
            messages.sort(key=lambda x: x.timestamp)
            
            return ChatSession(
                session_id=session_id,
                messages=messages,
                created_at=session_data["createdAt"],
                updated_at=session_data["updatedAt"],
                metadata=json.loads(session_data.get("metadata", "{}"))
            )
            
        except Exception as e:
            logger.error(f"Error getting session from Weaviate: {e}")
            raise DatabaseError(f"Failed to get session: {str(e)}")
    
    async def delete_session(
        self, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a chat session from Weaviate."""
        try:
            where_filter = {
                "path": ["sessionId"],
                "operator": "Equal",
                "valueString": session_id
            }
            
            if user_id:
                where_filter = {
                    "operator": "And",
                    "operands": [
                        where_filter,
                        {
                            "path": ["userId"],
                            "operator": "Equal",
                            "valueString": user_id
                        }
                    ]
                }
            
            # Delete session metadata
            session_result = self.client.batch.delete_objects(
                class_name=self.session_class,
                where=where_filter
            )
            
            # Delete all messages for this session
            message_result = self.client.batch.delete_objects(
                class_name=self.message_class,
                where=where_filter
            )
            
            return session_result["results"]["successful"] > 0
            
        except Exception as e:
            logger.error(f"Error deleting session from Weaviate: {e}")
            raise DatabaseError(f"Failed to delete session: {str(e)}")
    
    async def list_sessions(
        self, 
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """List chat sessions from Weaviate."""
        try:
            where_filter = None
            if user_id:
                where_filter = {
                    "path": ["userId"],
                    "operator": "Equal",
                    "valueString": user_id
                }
            
            query = self.client.query.get(self.session_class, [
                "sessionId", "userId", "createdAt", "updatedAt", "messageCount", "metadata"
            ]).with_limit(limit)
            
            if where_filter:
                query = query.with_where(where_filter)
                
            result = query.do()
            
            sessions = []
            for session_data in result["data"]["Get"][self.session_class]:
                session = ChatSession(
                    session_id=session_data["sessionId"],
                    messages=[],  # Don't load messages for list view
                    created_at=session_data["createdAt"],
                    updated_at=session_data["updatedAt"],
                    metadata={
                        "message_count": session_data.get("messageCount", 0),
                        **json.loads(session_data.get("metadata", "{}"))
                    }
                )
                sessions.append(session)
            
            return sessions[offset:offset + limit]  # Manual pagination
            
        except Exception as e:
            logger.error(f"Error listing sessions from Weaviate: {e}")
            return []
    
    async def add_message(
        self, 
        session_id: str, 
        message: ChatMessage,
        user_id: Optional[str] = None
    ) -> bool:
        """Add a message to an existing session."""
        try:
            message_uuid = self._generate_uuid(f"message_{session_id}_{message.id}")
            message_data = {
                "sessionId": session_id,
                "messageId": message.id,
                "role": message.role.value,
                "content": message.content,
                "timestamp": message.timestamp,
                "userId": user_id,
                "messageMetadata": json.dumps(message.metadata or {})
            }
            
            self.client.data_object.create(
                data_object=message_data,
                class_name=self.message_class,
                uuid=message_uuid
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to Weaviate: {e}")
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
            where_filter = {
                "path": ["sessionId"],
                "operator": "Equal",
                "valueString": session_id
            }
            
            if user_id:
                where_filter = {
                    "operator": "And",
                    "operands": [
                        where_filter,
                        {
                            "path": ["userId"],
                            "operator": "Equal",
                            "valueString": user_id
                        }
                    ]
                }
            
            result = self.client.batch.delete_objects(
                class_name=self.message_class,
                where=where_filter
            )
            
            return result["results"]["successful"] > 0
            
        except Exception as e:
            logger.error(f"Error clearing session messages from Weaviate: {e}")
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
            logger.error(f"Error updating session metadata in Weaviate: {e}")
            raise DatabaseError(f"Failed to update session metadata: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check Weaviate health."""
        try:
            self.client.cluster.get_nodes_status()
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
            search_query = self.client.query.get(self.message_class, [
                "content", "role", "sessionId", "timestamp"
            ]).with_near_text({
                "concepts": [query]
            }).with_limit(limit).with_additional(["distance"])
            
            if session_id:
                where_filter = {
                    "path": ["sessionId"],
                    "operator": "Equal",
                    "valueString": session_id
                }
                search_query = search_query.with_where(where_filter)
            
            result = search_query.do()
            
            search_results = []
            for match in result["data"]["Get"][self.message_class]:
                search_results.append({
                    "content": match["content"],
                    "role": match["role"],
                    "session_id": match["sessionId"],
                    "timestamp": match["timestamp"],
                    "score": 1 - match["_additional"]["distance"]  # Convert distance to similarity score
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing semantic search in Weaviate: {e}")
            return []
