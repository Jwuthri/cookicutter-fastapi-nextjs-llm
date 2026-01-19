# {{cookiecutter.project_name}} Backend

{{cookiecutter.description}}

A clean, simple FastAPI backend with LangChain integration for LLM-powered applications.

## ✨ Features

### Core Features
- **🚀 FastAPI**: Modern, fast web framework for building APIs
- **🔐 Clerk Authentication**: Enterprise-grade authentication with JWT
- **🗄️ Database**: SQLAlchemy async with PostgreSQL/SQLite support
- **🔗 LangChain Integration**: OpenRouter provider for LLM access
- **🤖 Agents Framework**: Modular agent structure with prompts, tools, and structured outputs
- **📊 Health & Metrics**: Simple health checks and metrics endpoints
- **📝 Structured Logging**: Request tracing and logging utilities

### LangChain & LLM Features
- **OpenRouter Provider**: Unified access to multiple LLM providers
- **Token Counting**: Accurate token counting utilities
- **Agent Framework**: Modular agent structure (agents/prompt/tool/structured_output)
- **Context Management**: Built-in context management agent
- **Tool Support**: LangChain tools for agent workflows

## 🏗️ Architecture

```
app/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration from environment variables
├── exceptions.py              # Exception handlers
│
├── api/                       # API endpoints
│   ├── v1/
│   │   ├── router.py         # Main API router
│   │   ├── auth.py           # Clerk authentication endpoints
│   │   ├── health.py         # Health check endpoints
│   │   └── metrics.py        # Metrics endpoints
│   ├── deps.py               # API-specific dependencies
│   └── response_wrapper.py   # API response utilities
│
├── agents/                    # LangChain agents framework
│   ├── agents/               # Agent implementations
│   │   └── context_manager.py
│   ├── prompt/               # Prompt templates
│   │   └── context_manager.py
│   ├── tool/                 # LangChain tools
│   │   └── context_manager.py
│   └── structured_output/    # Pydantic output models
│       └── context_manager.py
│
├── database/                  # Database layer
│   ├── base.py               # SQLAlchemy base
│   ├── session.py            # Async session management
│   ├── transaction.py        # Transaction utilities
│   ├── models/               # Database models
│   │   └── user.py           # User model (Clerk-based auth)
│   └── repositories/         # Data access layer
│       └── user.py           # User repository
│
├── infrastructure/            # Infrastructure layer
│   └── llm_provider.py       # OpenRouter LLM provider
│
├── models/                    # Pydantic API models
│   ├── base.py               # Base response models
│   └── user.py               # User API models
│
├── security/                  # Security utilities
│   └── clerk_auth.py         # Clerk authentication
│
├── middleware/                # Middleware
│   └── __init__.py           # Logging, CORS, security headers
│
├── utils/                     # Utilities
│   ├── logging.py            # Logging configuration
│   ├── token_counter.py      # Token counting utilities
│   ├── exceptions.py         # Exception utilities
│   ├── helpers.py            # Helper functions
│   └── retry.py              # Retry logic
│
├── cli/                       # CLI commands
│   ├── commands/             # CLI command modules
│   │   ├── database.py       # Database management
│   │   ├── health.py         # Health checks
│   │   ├── llm.py            # LLM testing/management
│   │   ├── logs.py           # Log viewing
│   │   ├── server.py         # Server management
│   │   ├── setup.py          # Setup utilities
│   │   └── worker.py         # Worker management (if needed)
│   └── main.py               # CLI entry point
│
└── examples/                  # Example code
    ├── langchain_example.py   # LangChain usage examples
    ├── agent_example.py       # Agent usage examples
    └── tool_example.py        # Tool usage examples
```

## 🚀 Quick Start

### Prerequisites

- **Python**: {{cookiecutter.python_version}}+
- **OpenRouter API Key**: Get one at https://openrouter.ai
- **Clerk Account**: Get one at https://clerk.dev (optional, for auth)

### 1. Configuration Setup

```bash
# Copy the configuration template
cp .env.template .env

# Edit your configuration
nano .env  # or use your preferred editor
```

**Required Settings:**

```bash
# OpenRouter API Key (required for LLM features)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Database (SQLite by default)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Clerk Authentication (optional)
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or using pip
pip install -e .
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or initialize database
python -m app.cli database init
```

### 4. Start the Server

```bash
# Development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Python directly
python -m app.main
```

### 5. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **🚀 Backend API** | http://localhost:8000 | Main API server |
| **📚 API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **🏥 Health Checks** | http://localhost:8000/api/v1/health/ | Service health monitoring |

## 📡 API Usage

### Health Checks

```bash
# Main health check
curl "http://localhost:8000/api/v1/health/"

# Readiness probe
curl "http://localhost:8000/api/v1/health/ready"

# Liveness probe
curl "http://localhost:8000/api/v1/health/live"
```

### Authentication (Clerk)

All authentication is handled by Clerk. Users authenticate via Clerk's frontend SDK, and the backend validates JWT tokens.

```bash
# Get current user profile (requires authentication)
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"

# Check authentication status (optional auth)
curl -X GET "http://localhost:8000/api/v1/auth/status" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"

# Get Clerk configuration for frontend
curl "http://localhost:8000/api/v1/auth/config"

# Validate JWT token
curl -X POST "http://localhost:8000/api/v1/auth/validate" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"

# Check Clerk configuration status
curl "http://localhost:8000/api/v1/auth/check-config"

# Authentication health check
curl "http://localhost:8000/api/v1/auth/health"
```

**Available Auth Endpoints:**

- `GET /api/v1/auth/me` - Get current user profile (requires auth)
- `GET /api/v1/auth/status` - Get auth status (optional auth)
- `GET /api/v1/auth/config` - Get Clerk config for frontend
- `GET /api/v1/auth/user/{user_id}` - Get user by ID (requires auth)
- `POST /api/v1/auth/validate` - Validate JWT token (requires auth)
- `GET /api/v1/auth/check-config` - Check Clerk configuration
- `GET /api/v1/auth/protected` - Example protected route (requires auth)
- `GET /api/v1/auth/health` - Auth system health check

### Metrics

```bash
# Get application metrics
curl "http://localhost:8000/api/v1/metrics/"

# Get metrics summary
curl "http://localhost:8000/api/v1/metrics/summary"
```

## 🤖 LangChain & Agents Usage

### Basic LangChain Example

```python
from app.infrastructure.llm_provider import OpenRouterProvider
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize provider
provider = OpenRouterProvider()

# Get LLM instance
llm = provider.get_llm(model_name="openai/gpt-4o-mini", temperature=0.7)

# Create chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()

# Use chain
response = chain.invoke({"input": "Hello!"})
print(response)
```

### Using Agents

```python
from app.agents.agents.context_manager import ContextManagerAgent, ContextCheckRequest
from app.infrastructure.llm_provider import OpenRouterProvider

# Initialize
provider = OpenRouterProvider()
agent = ContextManagerAgent(provider, model_name="openai/gpt-4o-mini")

# Check context
request = ContextCheckRequest(
    system_prompt="You are a helpful assistant.",
    history=[{"role": "user", "content": "Hello"}],
    current_item="New message",
    model_name="openai/gpt-4o-mini"
)

result = agent.check_context(request)
print(f"Total tokens: {result.total_tokens}")
print(f"Exceeds limit: {result.exceeds_limit}")
```

### Using Tools

```python
from app.agents.tool.context_manager import count_history_items, get_recent_items

# Use tools directly
history = [{"role": "user", "content": "Hello"}]
count = count_history_items.invoke({"history": history})

# Bind tools to LLM
from app.infrastructure.llm_provider import OpenRouterProvider

provider = OpenRouterProvider()
llm = provider.get_llm(model_name="openai/gpt-4o-mini")
llm_with_tools = llm.bind_tools([count_history_items, get_recent_items])

# LLM can now use these tools
response = llm_with_tools.invoke("Count items in my history")
```

### Token Counting

```python
from app.infrastructure.llm_provider import OpenRouterProvider
from app.utils.token_counter import count_tokens_llm, get_model_limits

provider = OpenRouterProvider()
llm = provider.get_llm(model_name="openai/gpt-4o-mini")

# Count tokens
text = "Hello, how are you?"
token_count = count_tokens_llm(llm, text)

# Get model limits
limits = get_model_limits(provider, "openai/gpt-4o-mini")
print(f"Context length: {limits['context_length']}")
print(f"Max completion: {limits['max_completion_tokens']}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_repository.py

# Run tests by marker
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m database          # Database tests only

# Run with verbose output
pytest -v

# Run specific test function
pytest tests/unit/test_user_repository.py::TestUserRepository::test_create_user

# Run tests matching a pattern
pytest -k "user"            # Tests with "user" in name

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Test Structure

```
tests/
├── conftest.py                    # Test fixtures and configuration
├── unit/                          # Unit tests (fast, isolated)
│   └── test_user_repository.py   # User repository tests
├── integration/                   # Integration tests
│   └── test_health_api.py        # API integration tests
└── performance/                   # Performance tests
    └── test_load_testing.py       # Load testing
```

### Test Coverage

The project aims for 80%+ test coverage. View coverage reports:

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Writing Tests

Tests use pytest with async support. Example:

```python
import pytest
from app.database.repositories import UserRepository

@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.database
class TestUserRepository:
    async def test_create_user(self, test_db_session):
        user = await UserRepository.create(
            db=test_db_session,
            clerk_id="user_test123",
            email="test@example.com"
        )
        assert user.clerk_id == "user_test123"
```

### Available Fixtures

- `test_db_session`: Async database session (in-memory SQLite)
- `test_user`: Pre-created test user with Clerk ID
- `client`: FastAPI test client with dependency overrides
- `test_settings`: Test-specific settings

### Test Markers

Use markers to categorize tests:

- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.database`: Database-dependent tests
- `@pytest.mark.slow`: Tests taking >5 seconds

## 📚 Examples

Check out the example files in `app/examples/`:

- **`langchain_example.py`**: Basic LangChain usage
- **`agent_example.py`**: Using agents
- **`tool_example.py`**: Using LangChain tools

Run examples:
```bash
python -m app.examples.langchain_example
python -m app.examples.agent_example
python -m app.examples.tool_example
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.template` for all available options.

### Key Settings

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# OpenRouter (for LLM)
OPENROUTER_API_KEY=your-key-here

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## 🏗️ Project Structure

### Agents Framework

The agents follow a modular structure:

```
agents/
├── agents/              # Agent implementations
├── prompt/              # Prompt templates
├── tool/                # LangChain tools
└── structured_output/   # Pydantic output models
```

Each agent has:
- **Agent**: Business logic implementation
- **Prompts**: System and user prompts
- **Tools**: LangChain tools the agent can use
- **Structured Outputs**: Type-safe Pydantic models

See `app/agents/README.md` for more details.

### Database

- **Models**: `User` model (Clerk-based authentication)
  - Uses `clerk_id` as the primary identifier
  - No password fields (authentication handled by Clerk)
  - Supports user preferences and metadata
- **Repositories**: `UserRepository` with async CRUD operations
- **Async**: Full async/await support

### Infrastructure

- **LLM Provider**: OpenRouter integration
- **Token Counter**: Token counting utilities
- **Model Info**: Context limits and model information

## 🔒 Security

- **Clerk Authentication**: JWT-based authentication (no password storage)
- **CORS**: Configurable CORS settings
- **Security Headers**: Automatic security headers
- **Input Validation**: Pydantic validation

## 📊 Monitoring

- **Health Checks**: `/api/v1/health/`
- **Metrics**: `/api/v1/metrics/`
- **Structured Logging**: Request tracing with correlation IDs

## 🚀 Production Deployment

### Docker

```bash
# Build image
docker build -t {{cookiecutter.project_slug}}-backend .

# Run container
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  {{cookiecutter.project_slug}}-backend
```

### Environment Variables

Required:
- `OPENROUTER_API_KEY`: OpenRouter API key
- `DATABASE_URL`: Database connection string

Optional:
- `CLERK_SECRET_KEY`: Clerk secret key
- `CLERK_PUBLISHABLE_KEY`: Clerk publishable key
- `DEBUG`: Set to `false` in production
- `LOG_LEVEL`: Logging level (INFO, WARNING, ERROR)

## 🐛 Troubleshooting

### Common Issues

**OpenRouter API Key not set:**
```bash
# Set in .env file
OPENROUTER_API_KEY=your-key-here
```

**Database connection issues:**
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from app.database.session import get_async_engine; import asyncio; asyncio.run(get_async_engine())"
```

**Import errors:**
```bash
# Make sure you're in the backend directory
cd backend

# Install dependencies
uv pip install -e .
```

**Clerk authentication not working:**
```bash
# Check Clerk configuration
curl "http://localhost:8000/api/v1/auth/check-config"

# Verify JWT token format
# Tokens should start with "eyJ" (base64 encoded JWT)
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Agents README**: `app/agents/README.md`
- **LangChain Docs**: https://python.langchain.com/
- **Clerk Docs**: https://clerk.com/docs

## 📄 License

MIT License

---

**Generated by [cookiecutter-fastapi-nextjs-llm](https://github.com/your-org/cookiecutter-fastapi-nextjs-llm)**
