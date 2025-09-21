"""
Configuration management for {{cookiecutter.project_name}}.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # App configuration
    app_name: str = "{{cookiecutter.project_name}}"
    app_version: str = "{{cookiecutter.version}}"
    description: str = "{{cookiecutter.description}}"
    environment: str = "development"
    debug: bool = False
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = {{cookiecutter.backend_port}}
    reload: bool = True
    workers: int = 1
    
    # API configuration
    api_v1_str: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:{{cookiecutter.frontend_port}}",
        "http://127.0.0.1:{{cookiecutter.frontend_port}}",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    allowed_hosts: List[str] = ["*"]
    
    # Database configuration
    {% if cookiecutter.include_database == "postgresql" %}
    database_url: Optional[str] = "postgresql://postgres:postgres@localhost:{{cookiecutter.postgres_port}}/{{cookiecutter.project_slug}}"
    {% elif cookiecutter.include_database == "sqlite" %}
    database_url: Optional[str] = "sqlite:///./data/{{cookiecutter.project_slug}}.db"
    {% else %}
    database_url: Optional[str] = None
    {% endif %}
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 100
    redis_socket_timeout: int = 5
    
    # Kafka configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "{{cookiecutter.project_slug}}_backend"
    kafka_auto_offset_reset: str = "latest"
    
    # RabbitMQ configuration
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_connection_timeout: int = 30
    
    # Agno + OpenRouter LLM configuration
    llm_provider: str = "openrouter"
    openrouter_api_key: Optional[str] = None
    default_model: str = "{{cookiecutter.default_model}}"
    max_tokens: int = 1000
    temperature: float = 0.7
    site_url: Optional[str] = None  # For OpenRouter referrer tracking
    
    # Agno Agent configuration
    use_agno_agents: bool = {% if cookiecutter.use_agno_agents == "yes" %}True{% else %}False{% endif %}
    agent_type: str = "{{cookiecutter.agent_type}}"  # single, multi-agent, workflow
    use_agno_memory: bool = True
    structured_outputs: bool = False
    agent_instructions: Optional[str] = None  # Default system prompt for agents
    
    # Vector Database configuration for memory
    vector_database: str = "{{cookiecutter.vector_database}}"
    memory_type: str = "{{cookiecutter.memory_type}}"  # vector, redis, hybrid, in-memory
    
    {% if cookiecutter.vector_database == "pinecone" %}
    # Pinecone configuration
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "gcp-starter"
    pinecone_index_name: str = "{{cookiecutter.project_slug}}-memory"
    {% elif cookiecutter.vector_database == "weaviate" %}
    # Weaviate configuration
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    weaviate_openai_api_key: Optional[str] = None  # For embeddings
    {% elif cookiecutter.vector_database == "qdrant" %}
    # Qdrant configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "{{cookiecutter.project_slug}}_memory"
    {% elif cookiecutter.vector_database == "chromadb" %}
    # ChromaDB configuration
    chromadb_path: str = "./data/chromadb"
    chromadb_collection_name: str = "{{cookiecutter.project_slug}}_memory"
    {% endif %}
    
    # WebSocket configuration
    websocket_enabled: bool = {% if cookiecutter.use_websockets == "yes" %}True{% else %}False{% endif %}
    websocket_heartbeat_interval: int = 30
    
    # Security configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days
    algorithm: str = "HS256"
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Session configuration
    session_expire_seconds: int = 86400  # 24 hours
    max_messages_per_session: int = 100
    
    # Cache configuration
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("debug")
    def set_debug(cls, v, values):
        return values.get("environment") == "development"
    
    @validator("reload")
    def set_reload(cls, v, values):
        return values.get("environment") == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
