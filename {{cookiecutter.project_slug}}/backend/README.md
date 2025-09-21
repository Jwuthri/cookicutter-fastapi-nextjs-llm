# {{cookiecutter.project_name}} Backend

{{cookiecutter.description}}

A modern, production-ready FastAPI backend for AI-powered chat applications with comprehensive LLM support, real-time messaging, and enterprise-grade architecture.

## 🚀 Features

### Core Features
- **🤖 Multiple LLM Providers**: OpenAI, Anthropic, HuggingFace, and custom implementations
- **💬 Real-time Chat**: WebSocket support for instant messaging
- **🧠 Conversation Memory**: Redis-based session storage with fallback to in-memory
- **📊 Message Queuing**: Kafka and RabbitMQ integration for scalable event processing
- **🔐 Security**: JWT authentication, rate limiting, and comprehensive middleware
- **📚 Auto Documentation**: Interactive Swagger/ReDoc API documentation

### Architecture & Design
- **🏗️ Clean Architecture**: Layered design with clear separation of concerns
- **🔄 Dependency Injection**: Comprehensive DI container for all services
- **🏭 Factory Pattern**: Flexible LLM provider switching
- **📦 Repository Pattern**: Abstracted data access with multiple backends
- **⚡ Service Layer**: Business logic separation
- **🛡️ Exception Handling**: Comprehensive error management

### Production Ready
- **🐳 Docker Support**: Multi-stage builds with development and production configurations
- **📊 Health Checks**: Comprehensive service monitoring endpoints
- **📝 Structured Logging**: Advanced logging with request tracing
- **🔒 Security Headers**: CORS, security middleware, and rate limiting
- **🎯 Performance**: Optimized for high throughput and low latency

## 🏗️ Architecture

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Application configuration
│   ├── dependencies.py         # Dependency injection container
│   ├── middleware.py           # Custom middleware stack
│   ├── exceptions.py           # Exception handlers
│   │
│   ├── api/                    # API layer
│   │   ├── deps.py            # API-specific dependencies
│   │   └── v1/                # API version 1
│   │       ├── router.py      # Main API router
│   │       ├── chat.py        # Chat endpoints
│   │       ├── completions.py # Text completion endpoints
│   │       └── health.py      # Health check endpoints
│   │
│   ├── core/                   # Business logic core
│   │   ├── llm/               # LLM implementations
│   │   │   ├── base.py        # Abstract LLM interface
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── huggingface_client.py
│   │   │   ├── custom_client.py
│   │   │   └── factory.py     # LLM provider factory
│   │   ├── memory/            # Conversation memory
│   │   │   ├── base.py        # Memory interface
│   │   │   ├── redis_memory.py
│   │   │   └── in_memory.py
│   │   └── security/          # Security components
│   │       ├── auth.py        # Authentication
│   │       └── rate_limit.py  # Rate limiting
│   │
│   ├── models/                 # Pydantic models
│   │   ├── chat.py            # Chat-related models
│   │   ├── completion.py      # Completion models
│   │   └── base.py            # Base/common models
│   │
│   ├── services/               # Business services
│   │   ├── chat_service.py    # Chat business logic
│   │   ├── completion_service.py
│   │   ├── conversation_service.py
│   │   ├── redis_client.py    # Redis integration
│   │   ├── kafka_client.py    # Kafka integration
│   │   └── rabbitmq_client.py # RabbitMQ integration
│   │
│   └── utils/                  # Utilities
│       ├── logging.py         # Logging configuration
│       └── helpers.py         # Helper functions
```

## 🚦 Quick Start

### Prerequisites

- **Python**: {{cookiecutter.python_version}}+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **uv**: Latest (automatically installed in Docker)

### 1. Development Setup

```bash
# Start development environment
./scripts/start.sh development

# Check service status
./scripts/status.sh

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f backend-dev
```

### 2. Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

**Required Environment Variables:**

{% if cookiecutter.llm_provider == "openai" %}
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
```
{% elif cookiecutter.llm_provider == "anthropic" %}
```bash
# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```
{% endif %}

```bash
# Security (IMPORTANT: Change in production!)
SECRET_KEY=your-secret-key-change-in-production

# Database (if using PostgreSQL)
{% if cookiecutter.include_database == "postgresql" %}
DATABASE_URL=postgresql://postgres:postgres@localhost:{{cookiecutter.postgres_port}}/{{cookiecutter.project_slug}}
{% endif %}
```

### 3. Access the Application

Once started, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:{{cookiecutter.backend_port}} | Main API server |
| **API Documentation** | http://localhost:{{cookiecutter.backend_port}}/docs | Interactive Swagger UI |
| **Health Check** | http://localhost:{{cookiecutter.backend_port}}/health | Service health status |
{% if cookiecutter.include_database == "postgresql" %}
| **pgAdmin** | http://localhost:5050 | Database management (admin@{{cookiecutter.project_slug}}.local / admin) |
{% endif %}
| **RabbitMQ Management** | http://localhost:15672 | Message queue management (guest/guest) |

## 🐳 Docker Usage

### Development

```bash
# Start all development services
./scripts/start.sh development

# Start with specific profiles (optional UIs)
docker-compose -f docker/docker-compose.dev.yml --profile kafka-ui --profile redis-ui up -d

# Stop services
./scripts/stop.sh development
```

### Production

```bash
# Deploy to production
./scripts/deploy.sh production

# Or start manually
./scripts/start.sh production

# Stop production services
./scripts/stop.sh production
```

## 📡 API Usage

### Chat Endpoint

```bash
# Send a chat message
curl -X POST "http://localhost:{{cookiecutter.backend_port}}/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "session_id": "optional-session-id"
  }'
```

### Text Completion

```bash
# Generate text completion
curl -X POST "http://localhost:{{cookiecutter.backend_port}}/api/v1/completions/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short story about AI",
    "max_tokens": 200,
    "temperature": 0.8
  }'
```

### Health Check

```bash
# Check service health
curl "http://localhost:{{cookiecutter.backend_port}}/api/v1/health/"
```

## 🔧 Configuration

### LLM Providers

The application supports multiple LLM providers:

{% if cookiecutter.llm_provider == "openai" %}
**OpenAI** (Current):
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4
```
{% elif cookiecutter.llm_provider == "anthropic" %}
**Anthropic** (Current):
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```
{% elif cookiecutter.llm_provider == "huggingface" %}
**HuggingFace** (Current):
```bash
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium
```
{% endif %}

**Switch Providers:**
```bash
# Change to different provider
LLM_PROVIDER=custom  # Uses mock responses for testing
```

### Memory Storage

**Redis** (Recommended):
```bash
REDIS_URL=redis://localhost:6379/0
```

**In-Memory** (Fallback):
- Automatically used when Redis is unavailable
- Development and testing only

### Database Configuration

{% if cookiecutter.include_database == "postgresql" %}
**PostgreSQL**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:{{cookiecutter.postgres_port}}/{{cookiecutter.project_slug}}
```
{% elif cookiecutter.include_database == "sqlite" %}
**SQLite**:
```bash
DATABASE_URL=sqlite:///./data/{{cookiecutter.project_slug}}.db
```
{% else %}
**No Database**:
- Uses in-memory storage
- Configure DATABASE_URL if needed
{% endif %}

## 🧪 Development

### Local Development (without Docker)

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Start the development server
uvicorn app.main:app --host 0.0.0.0 --port {{cookiecutter.backend_port}} --reload
```

### Running Tests

```bash
# Install test dependencies
uv pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Install development tools
uv pip install black isort flake8 mypy

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

## 📊 Monitoring

### Health Checks

The application provides comprehensive health checks:

- **`/health`**: Overall application health
- **`/api/v1/health/redis`**: Redis connectivity
- **`/api/v1/health/kafka`**: Kafka connectivity  
- **`/api/v1/health/rabbitmq`**: RabbitMQ connectivity
- **`/api/v1/health/ready`**: Kubernetes readiness probe
- **`/api/v1/health/live`**: Kubernetes liveness probe

### Logging

Structured logging with request tracing:

```python
# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f backend-dev

# Filter by service
docker-compose logs -f redis-dev kafka-dev
```

### Metrics

Integration points for monitoring:

- **Prometheus**: Metrics endpoint (configure as needed)
- **Grafana**: Visualization (configure as needed)
- **Jaeger**: Distributed tracing (configure as needed)

## 🚀 Deployment

### Production Deployment

```bash
# Quick deployment
./scripts/deploy.sh production

# With custom settings
ENVIRONMENT=production \
SECRET_KEY=your-production-secret \
OPENAI_API_KEY=your-api-key \
./scripts/deploy.sh production
```

### Environment Variables for Production

**Required**:
- `SECRET_KEY`: Strong random secret key
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM provider credentials
- `POSTGRES_PASSWORD`: Database password

**Optional**:
- `CORS_ORIGINS`: Allowed origins for CORS
- `RATE_LIMIT_REQUESTS`: Requests per minute limit
- `LOG_LEVEL`: Logging level (INFO, WARNING, ERROR)

### Scaling

**Horizontal Scaling**:
```bash
# Scale backend instances
docker-compose -f docker/docker-compose.yml up --scale backend=3 -d
```

**Load Balancing**:
- Use Nginx reverse proxy (included)
- Configure SSL certificates
- Add health check monitoring

## 🔒 Security

### Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **API Keys**: Use environment variables or secret management
3. **HTTPS**: Enable SSL/TLS in production (Nginx config provided)
4. **Rate Limiting**: Configure appropriate limits for your use case
5. **CORS**: Restrict origins to your domain
6. **Authentication**: Implement JWT or OAuth as needed

### Rate Limiting

```bash
# Configure rate limits
RATE_LIMIT_REQUESTS=100  # Requests per minute
RATE_LIMIT_WINDOW=60     # Time window in seconds
```

## 🐛 Troubleshooting

### Common Issues

**Port Conflicts**:
```bash
# Check port usage
lsof -i :{{cookiecutter.backend_port}}
netstat -an | grep {{cookiecutter.backend_port}}
```

**Service Not Starting**:
```bash
# Check logs
docker-compose logs service-name

# Restart services
./scripts/stop.sh && ./scripts/start.sh
```

**Database Connection Issues**:
```bash
# Test database connection
docker exec {{cookiecutter.project_slug}}_postgres_dev pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

**LLM API Issues**:
- Verify API keys are set correctly
- Check API rate limits and quotas
- Test with `curl` commands
- Switch to custom provider for testing

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debug
./scripts/start.sh development
```

### Getting Help

1. **Check Logs**: `docker-compose logs -f backend-dev`
2. **Health Status**: `./scripts/status.sh`
3. **API Documentation**: http://localhost:{{cookiecutter.backend_port}}/docs
4. **Service Status**: http://localhost:{{cookiecutter.backend_port}}/health

## 📚 API Documentation

Interactive API documentation is automatically generated and available at:

- **Swagger UI**: http://localhost:{{cookiecutter.backend_port}}/docs
- **ReDoc**: http://localhost:{{cookiecutter.backend_port}}/redoc
- **OpenAPI JSON**: http://localhost:{{cookiecutter.backend_port}}/openapi.json

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints for all functions
- Write comprehensive tests
- Update documentation
- Ensure Docker builds succeed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏢 Support

- **Documentation**: Check `/docs` endpoint
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Generated by [cookiecutter-fastapi-nextjs-llm](https://github.com/your-org/cookiecutter-fastapi-nextjs-llm)**
