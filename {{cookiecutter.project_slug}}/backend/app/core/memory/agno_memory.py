"""
Agno-based memory implementations for all vector databases.
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

try:
    from agno import Agent, Memory, VectorDB
    from agno.memory import ChatMemory, VectorMemory, HybridMemory
    from agno.vector_db import Pinecone, Weaviate, Qdrant, ChromaDB
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

from app.core.memory.base import MemoryInterface
from app.exceptions import ConfigurationError, ExternalServiceError
from app.utils.logging import get_logger

logger = get_logger("agno_memory")


class AgnoMemoryInterface(MemoryInterface):
    """Base class for Agno-based memory implementations."""
    
    def __init__(self, settings: Any):
        if not AGNO_AVAILABLE:
            raise ConfigurationError("Agno package not installed. Install with: pip install agno")
        
        self.settings = settings
        self.memory: Optional[Memory] = None
        self._initialized = False
    
    @abstractmethod
    async def _create_agno_memory(self) -> Memory:
        """Create the Agno memory instance."""
        pass
    
    async def initialize(self):
        """Initialize the Agno memory system."""
        if not self._initialized:
            try:
                self.memory = await self._create_agno_memory()
                self._initialized = True
                logger.info(f"Initialized {self.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
                raise ConfigurationError(f"Memory initialization failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.memory:
            try:
                if hasattr(self.memory, 'close'):
                    await self.memory.close()
                self._initialized = False
                logger.debug(f"Cleaned up {self.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Error cleaning up {self.__class__.__name__}: {e}")
    
    # MemoryInterface implementation using Agno
    
    async def store_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a message using Agno's memory system."""
        if not self._initialized:
            await self.initialize()
        
        try:
            message_data = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                **(metadata or {})
            }
            
            # Use Agno's built-in message storage
            await self.memory.add_message(
                session_id=session_id,
                role=role,
                content=content,
                metadata=message_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing message in session {session_id}: {e}")
            raise ExternalServiceError(f"Failed to store message: {e}", service="agno_memory")
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve messages using Agno's memory system."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use Agno's built-in message retrieval
            messages = await self.memory.get_messages(
                session_id=session_id,
                limit=limit or 50
            )
            
            # Convert Agno messages to our format
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", datetime.utcnow().isoformat()),
                    "metadata": msg.get("metadata", {})
                }
                formatted_messages.append(formatted_msg)
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages for session {session_id}: {e}")
            raise ExternalServiceError(f"Failed to retrieve messages: {e}", service="agno_memory")
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear session using Agno's memory system."""
        if not self._initialized:
            await self.initialize()
        
        try:
            await self.memory.clear_session(session_id)
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session {session_id}: {e}")
            raise ExternalServiceError(f"Failed to clear session: {e}", service="agno_memory")
    
    async def search_similar(self, query: str, session_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content using Agno's vector search."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use Agno's semantic search if available
            if hasattr(self.memory, 'search'):
                results = await self.memory.search(
                    query=query,
                    session_id=session_id,
                    limit=limit
                )
                
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                        "metadata": result.get("metadata", {}),
                        "session_id": result.get("session_id")
                    }
                    formatted_results.append(formatted_result)
                
                return formatted_results
            else:
                # Fallback to basic message retrieval
                messages = await self.get_messages(session_id or "default", limit=limit)
                return [{"content": msg["content"], "score": 1.0, "metadata": msg.get("metadata", {})} for msg in messages[-limit:]]
            
        except Exception as e:
            logger.error(f"Error searching similar content: {e}")
            raise ExternalServiceError(f"Failed to search: {e}", service="agno_memory")
    
    async def health_check(self) -> bool:
        """Check if Agno memory is healthy."""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Test basic functionality
            test_session = "health_check_test"
            await self.store_message(test_session, "system", "health check", {"test": True})
            messages = await self.get_messages(test_session, limit=1)
            await self.clear_session(test_session)
            
            return len(messages) > 0
            
        except Exception as e:
            logger.error(f"Agno memory health check failed: {e}")
            return False


class AgnoPineconeMemory(AgnoMemoryInterface):
    """Agno-based Pinecone memory implementation."""
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno memory with Pinecone vector store (PERSISTENT)."""
        pinecone_config = {
            "api_key": self.settings.get_secret("pinecone_api_key"),
            "environment": self.settings.pinecone_environment,
            "index_name": self.settings.pinecone_index_name,
            # Add namespace for isolation and persistence
            "namespace": f"{getattr(self.settings, 'app_name', 'app')}_persistent"
        }
        
        if not pinecone_config["api_key"]:
            raise ConfigurationError("Pinecone API key not configured")
        
        # Create Pinecone vector store with persistence settings
        vector_db = Pinecone(**pinecone_config)
        
        # Create persistent Redis storage for chat memory
        try:
            from agno.storage import RedisStorage
            redis_storage = RedisStorage(
                host=getattr(self.settings, 'redis_host', 'localhost'),
                port=getattr(self.settings, 'redis_port', 6379),
                db=getattr(self.settings, 'redis_db', 2),  # Separate DB for Agno
                key_prefix="agno_pinecone:",
                ttl=60 * 60 * 24 * 30  # 30 days retention
            )
            
            chat_memory = ChatMemory(
                storage=redis_storage,  # PERSISTENT REDIS BACKEND
                max_messages=1000,
                compress_when_full=True
            )
        except (ImportError, Exception) as e:
            logger.warning(f"Redis storage not available, using non-persistent chat memory: {e}")
            chat_memory = ChatMemory()
        
        # Create hybrid memory (PERSISTENT chat + vector)
        return HybridMemory(
            chat_memory=chat_memory,
            vector_memory=VectorMemory(
                vector_db=vector_db,
                max_items=100000,      # Large capacity for persistence  
                auto_save_interval=60  # Save every minute
            ),
            embed_model="text-embedding-3-small",
            
            # Persistence settings
            sync_interval=120,         # Sync between memories every 2 minutes
            auto_promote_threshold=0.8 # Promote important chat to vector storage
        )


class AgnoWeaviateMemory(AgnoMemoryInterface):
    """Agno-based Weaviate memory implementation."""
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno memory with Weaviate vector store."""
        weaviate_config = {
            "url": self.settings.weaviate_url,
            "api_key": self.settings.get_secret("weaviate_api_key"),
            "openai_api_key": self.settings.get_secret("weaviate_openai_api_key"),
        }
        
        # Create Weaviate vector store
        vector_db = Weaviate(**weaviate_config)
        
        return HybridMemory(
            chat_memory=ChatMemory(),
            vector_memory=VectorMemory(vector_db=vector_db),
            embed_model="text-embedding-3-small"
        )


class AgnoQdrantMemory(AgnoMemoryInterface):
    """Agno-based Qdrant memory implementation."""
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno memory with Qdrant vector store."""
        qdrant_config = {
            "url": self.settings.qdrant_url,
            "api_key": self.settings.get_secret("qdrant_api_key"),
            "collection_name": self.settings.qdrant_collection_name,
        }
        
        # Create Qdrant vector store
        vector_db = Qdrant(**qdrant_config)
        
        return HybridMemory(
            chat_memory=ChatMemory(),
            vector_memory=VectorMemory(vector_db=vector_db),
            embed_model="text-embedding-3-small"
        )


class AgnoChromaMemory(AgnoMemoryInterface):
    """Agno-based ChromaDB memory implementation."""
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno memory with ChromaDB vector store."""
        chroma_config = {
            "path": self.settings.chromadb_path,
            "collection_name": self.settings.chromadb_collection_name,
        }
        
        # Create ChromaDB vector store
        vector_db = ChromaDB(**chroma_config)
        
        return HybridMemory(
            chat_memory=ChatMemory(),
            vector_memory=VectorMemory(vector_db=vector_db),
            embed_model="text-embedding-3-small"
        )


class AgnoChatMemory(AgnoMemoryInterface):
    """Agno-based chat-only memory (no vector storage)."""
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno chat memory only."""
        return ChatMemory()


class AgnoRedisMemory(AgnoMemoryInterface):
    """Agno-based Redis memory implementation."""
    
    def __init__(self, settings: Any, redis_client=None):
        super().__init__(settings)
        self.redis_client = redis_client
    
    async def _create_agno_memory(self) -> Memory:
        """Create Agno memory with Redis backend (PERSISTENT)."""
        try:
            from agno.storage import RedisStorage
            
            # Create persistent Redis storage for Agno
            redis_storage = RedisStorage(
                url=self.settings.redis_url,
                
                # Persistence configuration  
                key_prefix="agno_redis:",
                ttl=60 * 60 * 24 * 30,  # 30 days retention
                
                # Redis persistence settings (survives restarts)
                persistence_config={
                    "save": "900 1 300 10 60 10000",  # RDB snapshots
                    "appendonly": "yes",               # AOF for durability
                    "appendfsync": "everysec"          # Sync every second
                }
            )
            
            # Create chat memory with persistent Redis storage
            memory = ChatMemory(
                storage=redis_storage,      # PERSISTENT BACKEND
                max_messages=2000,          # More messages since it's persistent
                compress_when_full=True,
                session_ttl=60 * 60 * 24 * 30,  # 30 day session retention
                
                # Additional persistence settings
                auto_save_interval=30,      # Save every 30 seconds
                batch_operations=True       # Batch Redis operations for efficiency
            )
            
        except ImportError:
            logger.warning("Agno RedisStorage not available, falling back to basic Redis connection")
            
            # Fallback to basic Redis (still can be persistent if Redis is configured)
            memory = ChatMemory()
            
            # Try to configure Redis backend if supported
            if hasattr(memory, 'set_backend'):
                redis_config = {
                    "url": self.settings.redis_url,
                    "key_prefix": "agno_redis:",
                    "ttl": 60 * 60 * 24 * 30
                }
                memory.set_backend('redis', **redis_config)
        
        return memory


class AgnoMemoryFactory:
    """Factory for creating Agno-based memory instances."""
    
    MEMORY_PROVIDERS = {
        "pinecone": AgnoPineconeMemory,
        "weaviate": AgnoWeaviateMemory,
        "qdrant": AgnoQdrantMemory,
        "chromadb": AgnoChromaMemory,
        "chat": AgnoChatMemory,
        "redis": AgnoRedisMemory,
    }
    
    @classmethod
    async def create_memory(
        self, 
        provider: str, 
        settings: Any, 
        redis_client=None
    ) -> AgnoMemoryInterface:
        """Create an Agno memory instance based on provider."""
        if not AGNO_AVAILABLE:
            raise ConfigurationError(
                "Agno is not available. Install with: pip install agno"
            )
        
        provider = provider.lower()
        
        if provider not in self.MEMORY_PROVIDERS:
            available_providers = ", ".join(self.MEMORY_PROVIDERS.keys())
            raise ConfigurationError(
                f"Unsupported Agno memory provider: {provider}. "
                f"Available providers: {available_providers}"
            )
        
        memory_class = self.MEMORY_PROVIDERS[provider]
        
        # Special handling for Redis memory
        if provider == "redis" and redis_client:
            memory_instance = memory_class(settings, redis_client)
        else:
            memory_instance = memory_class(settings)
        
        # Initialize the memory
        await memory_instance.initialize()
        
        logger.info(f"Created Agno memory provider: {provider}")
        return memory_instance
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available Agno memory providers."""
        return list(cls.MEMORY_PROVIDERS.keys())
    
    @classmethod
    def validate_provider_config(cls, provider: str, settings: Any) -> Dict[str, Any]:
        """Validate configuration for a specific provider."""
        validation_report = {
            "provider": provider,
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        provider = provider.lower()
        
        if provider == "pinecone":
            if not settings.get_secret("pinecone_api_key"):
                validation_report["errors"].append("Pinecone API key is required")
            if not settings.pinecone_index_name:
                validation_report["errors"].append("Pinecone index name is required")
                
        elif provider == "weaviate":
            if not settings.weaviate_url:
                validation_report["errors"].append("Weaviate URL is required")
            if not settings.get_secret("weaviate_openai_api_key"):
                validation_report["warnings"].append("OpenAI API key recommended for embeddings")
                
        elif provider == "qdrant":
            if not settings.qdrant_url:
                validation_report["errors"].append("Qdrant URL is required")
            if not settings.qdrant_collection_name:
                validation_report["errors"].append("Qdrant collection name is required")
                
        elif provider == "chromadb":
            if not settings.chromadb_path:
                validation_report["errors"].append("ChromaDB path is required")
            if not settings.chromadb_collection_name:
                validation_report["errors"].append("ChromaDB collection name is required")
        
        validation_report["valid"] = len(validation_report["errors"]) == 0
        return validation_report
