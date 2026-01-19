# {{cookiecutter.project_name}}

> 🤖 **Modern AI Chat Application** built with **FastAPI** + **Next.js** + **OpenRouter** + **Clerk**

A simple, production-ready AI chat application featuring unified access to 500+ language models via OpenRouter, Clerk authentication, and a terminal-style interface.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-500%2B%20models-green?style=flat)](https://openrouter.ai)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178c6?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed?style=flat&logo=docker)](https://www.docker.com)

---

## 🌟 **Features**

### 🧠 **AI Capabilities**
- **500+ Models** via [OpenRouter](https://openrouter.ai) (GPT-5, Claude 3.7, Gemini 2.5 Pro, Llama 3.3, etc.)
- **LangChain Integration** for LLM interactions
- **Simple Q&A Interface** - Terminal-style chat UI
- **Stateless Conversations** - No session storage, reload resets

### 🔐 **Authentication**
- **Clerk Integration** - Google OAuth authentication
- **JWT Token Validation** - Secure API access
- **User Profile Management** - Clerk-based user system

### 🚀 **Production-Ready Architecture**
- **FastAPI Backend** with async/await support
- **Next.js Frontend** with App Router and TypeScript
- **Docker Compose** setup for development and production
- **Health Checks** and monitoring endpoints

### 🔧 **Developer Experience**
- **`uv`** for ultra-fast Python dependency management
- **Hot Reload** in development
- **Comprehensive Logging** with structured logging
- **Type Safety** with Pydantic and TypeScript

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │────│   FastAPI       │────│   OpenRouter    │
│   Frontend      │    │   Backend       │    │   LLM Service   │
│                 │    │                 │    │                 │
│ • TypeScript    │    │ • Python 3.11+ │    │ • 500+ Models   │
│ • Tailwind CSS  │    │ • Async/Await   │    │ • LangChain     │
│ • Clerk Auth    │    │ • Pydantic      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │                         │
            ┌───────▼──────┐         ┌───────▼──────┐
            │ PostgreSQL/  │         │   Clerk      │
            │ SQLite       │         │   Auth       │
            └──────────────┘         └──────────────┘
```

---

## 🚀 **Quick Start**

### 1. **Prerequisites**
```bash
# Install uv (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Node.js 18+
# https://nodejs.org/

# Install Docker & Docker Compose (optional)
# https://docs.docker.com/get-docker/
```

### 2. **Environment Setup**
```bash
# Copy environment files
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env.local

# Set your API keys in backend/.env
OPENROUTER_API_KEY=your_openrouter_key_here

# Set Clerk keys
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key

# Set Clerk publishable key in frontend/.env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
NEXT_PUBLIC_API_URL=http://localhost:{{cookiecutter.backend_port}}
```

### 3. **Start with Docker Compose** ⚡
```bash
# Start all services (recommended for first run)
docker-compose up -d
```

### 4. **Manual Development Setup** 🛠️
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port {{cookiecutter.backend_port}}

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 5. **Access Your Application** 🎉
- **Frontend**: http://localhost:{{cookiecutter.frontend_port}}
- **Backend API**: http://localhost:{{cookiecutter.backend_port}}
- **API Docs**: http://localhost:{{cookiecutter.backend_port}}/docs
- **ReDoc**: http://localhost:{{cookiecutter.backend_port}}/redoc

---

## 🤖 **AI Model Selection**

Choose from 500+ models available through OpenRouter:

```python
# Latest and greatest models
"gpt-5"                          # OpenAI's latest
"anthropic/claude-3.7-sonnet"    # Anthropic's most capable
"google/gemini-2.5-pro"          # Google's flagship

# Production workhorses
"openai/gpt-4o"                  # Reliable and fast
"anthropic/claude-3.5-sonnet"    # Great for reasoning
"google/gemini-1.5-pro"          # Excellent context window

# Fast and efficient
"openai/gpt-4o-mini"             # Quick responses (default)
"anthropic/claude-3-haiku"       # Speed optimized
"google/gemini-1.5-flash"        # Ultra fast
```

---

## 📚 **API Endpoints**

### **Authentication (Clerk)**
```bash
# Get current user profile (requires auth)
GET /api/v1/auth/me

# Check authentication status (optional auth)
GET /api/v1/auth/status

# Get Clerk configuration for frontend
GET /api/v1/auth/config

# Get user by ID (requires auth)
GET /api/v1/auth/user/{user_id}

# Validate JWT token (requires auth)
POST /api/v1/auth/validate

# Check Clerk configuration status
GET /api/v1/auth/check-config

# Example protected route (requires auth)
GET /api/v1/auth/protected

# Authentication health check
GET /api/v1/auth/health
```

### **Chat**
```bash
# Send a message to the LLM (requires auth)
POST /api/v1/chat
{
  "message": "Explain quantum computing",
  "model": "openai/gpt-4o-mini",  # optional
  "temperature": 0.7              # optional
}

# Response
{
  "response": "Quantum computing is...",
  "model_used": "openai/gpt-4o-mini"
}
```

### **Health & Metrics**
```bash
# Main health check
GET /api/v1/health/

# Readiness probe
GET /api/v1/health/ready

# Liveness probe
GET /api/v1/health/live

# Application metrics
GET /api/v1/metrics/

# Metrics summary
GET /api/v1/metrics/summary
```

---

## 🔧 **Configuration**

### **Backend Settings** (`backend/.env`)
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

### **Frontend Settings** (`frontend/.env.local`)
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:{{cookiecutter.backend_port}}

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
```

---

## 🚢 **Deployment**

### **Using Docker** (Recommended)
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### **Manual Deployment**
```bash
# Backend
cd backend
uv pip install -e .
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
npm run build
npm start
```

### **Environment Variables for Production**
- Set `DEBUG=false`
- Configure proper `CORS_ORIGINS`
- Set up SSL/TLS certificates
- Use managed database services (PostgreSQL recommended)
- Set production Clerk keys

---

## 📁 **Project Structure**

```
{{cookiecutter.project_slug}}/
├── 📁 backend/                 # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/v1/         # API routes
│   │   │   ├── auth.py        # Clerk authentication endpoints
│   │   │   ├── chat.py        # LLM chat endpoint
│   │   │   ├── health.py      # Health check endpoints
│   │   │   └── metrics.py     # Metrics endpoints
│   │   ├── 📁 agents/         # LangChain agents framework
│   │   ├── 📁 database/       # Database layer
│   │   │   ├── models/        # SQLAlchemy models (User)
│   │   │   └── repositories/ # Data access layer
│   │   ├── 📁 infrastructure/ # Infrastructure (LLM provider)
│   │   ├── 📁 models/         # Pydantic API models
│   │   ├── 📁 security/       # Clerk authentication
│   │   └── 📁 utils/          # Utilities
│   ├── 📁 docker/             # Docker configurations
│   └── 📄 pyproject.toml       # Python dependencies (uv)
│
├── 📁 frontend/               # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/            # Next.js App Router
│   │   │   └── page.tsx       # Terminal chat interface
│   │   ├── 📁 components/     # React components
│   │   ├── 📁 lib/            # Utilities & API client
│   │   └── 📁 hooks/          # Custom React hooks
│   └── 📄 package.json       # Node.js dependencies
│
├── 📄 docker-compose.yml     # Development services
└── 📄 README.md              # This file
```

---

## 🧪 **Development**

### **Running Tests**
```bash
# Backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### **Code Quality**
```bash
# Backend linting & formatting
cd backend
black .
isort .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### **Database Migrations**
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## 🔍 **Monitoring & Health Checks**

- **Health Check**: `GET /api/v1/health/`
- **Metrics**: `GET /api/v1/metrics/`
- **Auth Health**: `GET /api/v1/auth/health`

---

## 🤝 **Contributing**

### 🔧 **Setup Pre-commit Hooks**

We use pre-commit hooks to ensure code quality. Set them up before making changes:

```bash
# Install and setup pre-commit hooks
./scripts/setup-pre-commit.sh

# Or manually:
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

The hooks will automatically check:
- **Python**: Black formatting, autoflake unused import removal, isort import sorting, flake8 linting, mypy type checking
- **Frontend**: Prettier formatting, ESLint linting
- **Security**: Private key scanning
- **General**: Trailing whitespace, file endings, YAML/JSON validation

### 🚀 **Contribution Steps**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. **Setup pre-commit hooks**: `./scripts/setup-pre-commit.sh`
4. Make your changes
5. Run tests: `pytest`
6. Commit: `git commit -m 'Add amazing feature'` (pre-commit hooks will run automatically)
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **[OpenRouter](https://openrouter.ai)** - Unified access to 500+ AI models
- **[Clerk](https://clerk.com)** - Authentication and user management
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Next.js](https://nextjs.org)** - React framework for production
- **[LangChain](https://python.langchain.com)** - LLM framework
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package manager

---

## 📞 **Support**

- 📧 **Email**: {{cookiecutter.author_email}}
- 🐛 **Issues**: [GitHub Issues](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}/wiki)

---

<div align="center">

**Built with ❤️ using the latest AI technologies**

[🔀 OpenRouter](https://openrouter.ai) • [🔐 Clerk](https://clerk.com) • [⚡ FastAPI](https://fastapi.tiangolo.com) • [⚛️ Next.js](https://nextjs.org)

</div>
