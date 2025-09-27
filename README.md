# 🍪 Cookiecutter FastAPI + Next.js + Agno + OpenRouter

> **Modern AI Agent Application Template** - Generate production-ready AI agent apps in seconds!

A powerful [Cookiecutter](https://cookiecutter.readthedocs.io/) template for creating modern AI agent applications with **FastAPI**, **Next.js**, **Agno framework**, and **OpenRouter** for unified access to 500+ language models.

[![Cookiecutter](https://img.shields.io/badge/cookiecutter-template-D4AA00?style=flat&logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org)
[![Agno](https://img.shields.io/badge/Agno-2.0+-blue?style=flat)](https://docs.agno.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-500%2B%20models-green?style=flat)](https://openrouter.ai)

---

## 🌟 **What You Get**

This cookiecutter template generates a complete, production-ready AI agent application with:

### 🤖 **AI Agent Capabilities**
- **[Agno Framework](https://docs.agno.com)** - Advanced AI agents with memory, tools, and workflows
- **[OpenRouter](https://openrouter.ai)** - Unified access to 500+ models (GPT-5, Claude 3.7, Gemini 2.5 Pro, etc.)
- **Multi-Agent Systems** - Single agents, multi-agent teams, or step-based workflows
- **Built-in Memory** - Vector databases with semantic search + Redis for fast access

### 🏗️ **Modern Architecture**
- **FastAPI Backend** - Python 3.11+ with async/await, type hints, auto-documentation
- **Next.js Frontend** - React with App Router, TypeScript, modern dark theme
- **Authentication** - Clerk.com integration with Google social login
- **Vector Databases** - Pinecone, Weaviate, Qdrant, or ChromaDB for AI memory
- **WebSocket Support** - Real-time communication for chat interfaces
- **Docker Ready** - Complete containerization with Docker Compose

### ⚡ **Developer Experience**
- **[uv](https://docs.astral.sh/uv/)** - Ultra-fast Python package management
- **TypeScript** - Full type safety across frontend and backend
- **Hot Reload** - Fast development iteration
- **Comprehensive Tests** - Unit and integration testing setup
- **Production Deployment** - Scripts and configurations included

---

## 🚀 **Quick Start**

### 1. **Install Cookiecutter**
```bash
# Using pip
pip install cookiecutter

# Using uv (recommended)
uv tool install cookiecutter

# Using conda
conda install cookiecutter
```

### 2. **Generate Your Project**
```bash
cookiecutter https://github.com/Jwuthri/cookicutter-fastapi-nextjs-llm.git
```

### 3. **Answer the Prompts**
```bash
project_name [My AI Agent App]: Awesome AI Assistant
project_slug [awesome-ai-assistant]:
description [A FastAPI + Next.js AI agent application]: My awesome AI-powered assistant
author_name [Your Name]: John Doe
author_email [your.email@example.com]: john@example.com
version [0.1.0]:
python_version [3.11]:
node_version [18]:
use_websockets [yes]:
include_database [postgresql]:
default_model [gpt-4]: gpt-5
vector_database [pinecone]:
use_agno_agents [yes]:
agent_type [single]: multi-agent
memory_type [hybrid]:
frontend_port [3000]:
backend_port [8000]:
```

### 4. **Start Your AI Agent App**
```bash
cd awesome-ai-assistant
docker-compose up -d
```

🎉 **Your AI agent app is running at http://localhost:3000**

---

## 📋 **Configuration Options**

| Option | Description | Choices |
|--------|-------------|---------|
| `project_name` | Human-readable project name | Any string |
| `project_slug` | URL/folder-friendly name | Auto-generated |
| `description` | Project description | Any string |
| `default_model` | Default AI model | `gpt-4`, `claude-3-5-sonnet`, `gemini-2.5-pro`, `gpt-5`, `custom` |
| `vector_database` | Vector DB for AI memory | `pinecone`, `weaviate`, `qdrant`, `chromadb`, `none` |
| `use_agno_agents` | Enable Agno agent framework | `yes`, `no` |
| `agent_type` | Type of agent system | `single`, `multi-agent`, `workflow` |
| `memory_type` | Memory system type | `vector`, `redis`, `hybrid`, `in-memory` |
| `use_websockets` | Enable WebSocket support | `yes`, `no` |
| `include_database` | Database backend | `postgresql`, `sqlite`, `none` |
| `python_version` | Python version | `3.11`, `3.12` |
| `node_version` | Node.js version | `18`, `20` |

---

## 🎯 **Use Cases**

This template is perfect for building:

### 🤖 **AI Chatbots & Assistants**
- Customer support bots with memory
- Personal AI assistants
- Writing and editing tools
- Research and analysis helpers

### 🏢 **Business Applications**
- Document Q&A systems
- Meeting summarization tools
- CRM integration assistants
- Data analysis platforms

### 🎓 **Educational Tools**
- Tutoring applications
- Language learning assistants
- Research helpers
- Interactive learning platforms

### 🛠️ **Developer Tools**
- Code generation assistants
- API documentation generators
- Debug helpers
- Architecture advisors

---

## 📁 **Generated Project Structure**

```
your-ai-agent-app/
├── 📁 backend/                 # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/v1/         # API routes (chat, completions, health)
│   │   ├── 📁 core/           # Core business logic
│   │   │   ├── 📁 llm/        # Agno + OpenRouter integration
│   │   │   ├── 📁 memory/     # Vector & Redis memory systems
│   │   │   └── 📁 security/   # Authentication & rate limiting
│   │   ├── 📁 models/         # Pydantic data models
│   │   ├── 📁 services/       # Business logic services
│   │   └── 📄 main.py         # FastAPI application entry point
│   ├── 📁 docker/             # Docker configurations
│   ├── 📁 scripts/            # Deployment and utility scripts
│   ├── 📄 pyproject.toml      # Python dependencies (uv)
│   └── 📄 README.md           # Backend documentation
│
├── 📁 frontend/               # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/            # Next.js App Router
│   │   │   ├── 📁 chat/       # Chat interface pages
│   │   │   └── 📄 page.tsx    # Homepage
│   │   ├── 📁 components/     # React components
│   │   │   ├── 📁 ui/         # Base UI components (Button, Input, etc.)
│   │   │   ├── 📁 chat/       # Chat-specific components
│   │   │   └── 📁 providers/  # React context providers
│   │   ├── 📁 hooks/          # Custom React hooks
│   │   ├── 📁 lib/            # Utilities & API client
│   │   └── 📁 types/          # TypeScript type definitions
│   ├── 📄 package.json       # Node.js dependencies
│   ├── 📄 tailwind.config.js # Tailwind CSS configuration
│   └── 📄 README.md          # Frontend documentation
│
├── 📄 docker-compose.yml     # Development environment
├── 📄 docker-compose.prod.yml # Production deployment
└── 📄 README.md              # Main project documentation
```

---

## 🔧 **Development Workflow**

### **After Generation**
1. **Set up API keys** in `backend/.env`
2. **Choose your AI models** (GPT-5, Claude 3.7, Gemini 2.5 Pro, etc.)
3. **Configure vector database** (Pinecone, Weaviate, Qdrant, ChromaDB)
4. **Customize agent behavior** in the Agno configuration
5. **Design your chat interface** in the Next.js frontend

### **Key Files to Customize**
- `backend/app/core/llm/openrouter_client.py` - AI agent configuration
- `frontend/src/components/chat/` - Chat interface components
- `backend/app/config.py` - Application settings
- `frontend/src/app/page.tsx` - Homepage and routing

---

## 🌍 **AI Model Ecosystem**

Access **500+ models** through OpenRouter:

### **Latest & Greatest**
- **GPT-5** - OpenAI's newest flagship model
- **Claude 3.7 Sonnet** - Anthropic's most capable model
- **Gemini 2.5 Pro** - Google's multimodal powerhouse

### **Production Workhorses**
- **GPT-4o** - Fast and reliable for most tasks
- **Claude 3.5 Sonnet** - Excellent reasoning capabilities
- **Gemini 1.5 Pro** - Great context window (2M tokens)

### **Fast & Efficient**
- **GPT-4o Mini** - Quick responses, lower cost
- **Claude 3 Haiku** - Speed-optimized interactions
- **Gemini 1.5 Flash** - Ultra-fast processing

### **Open Source Leaders**
- **Llama 3.3 70B** - Meta's powerful open model
- **DeepSeek Chat** - Competitive open alternative
- **Qwen 2.5 72B** - Strong multilingual capabilities

---

## 🧩 **Extensions & Integrations**

The generated project supports easy integration with:

### **Databases**
- PostgreSQL, SQLite (built-in)
- MongoDB, MySQL (add manually)
- Supabase, PlanetScale (cloud)

### **Authentication**
- Clerk.com (built-in with Google social login)
- JWT token verification (built-in)
- OAuth 2.0, Auth0 (add manually)
- Firebase Auth (third-party)

### **Deployment**
- Docker + Docker Compose (built-in)
- Kubernetes, AWS ECS (container orchestration)
- Vercel, Railway, Render (platform deployment)

### **Monitoring**
- Prometheus metrics (built-in)
- Grafana, DataDog (monitoring)
- Sentry (error tracking)

---

## 🚀 **Deployment Options**

### **1. Docker Compose** (Simplest)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **2. Cloud Platforms**
- **Frontend**: Vercel, Netlify, Railway
- **Backend**: Railway, Render, Google Cloud Run
- **Full Stack**: AWS, Google Cloud, Azure

### **3. VPS/Self-Hosted**
```bash
# Use the deployment script
./backend/scripts/deploy.sh
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how:

1. **Fork this repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Test your changes**: Generate a project and test it works
4. **Update documentation** if needed
5. **Submit a Pull Request**

### **Development Setup**
```bash
git clone https://github.com/julienwuthrich/cookiecutter-fastapi-nextjs-llm
cd cookiecutter-fastapi-nextjs-llm

# Test the template
cookiecutter . --no-input
cd my-ai-agent-app
docker-compose up -d
```

---

## 📚 **Resources**

### **Documentation**
- [Agno Framework Docs](https://docs.agno.com) - AI agent framework
- [OpenRouter API](https://openrouter.ai/docs) - Model access documentation
- [FastAPI Docs](https://fastapi.tiangolo.com) - Backend framework
- [Next.js Docs](https://nextjs.org/docs) - Frontend framework
- [uv Documentation](https://docs.astral.sh/uv/) - Python package manager

### **Tutorials**
- [Building AI Agents with Agno](https://docs.agno.com/examples)
- [OpenRouter Model Comparison](https://openrouter.ai/models)
- [Vector Database Guide](https://example.com) - Choosing the right vector DB
- [Production Deployment Guide](https://example.com) - Deploy your AI app

---

## ⭐ **Star History**

If this template helps you build awesome AI applications, please give it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=julienwuthrich/cookiecutter-fastapi-nextjs-llm&type=Date)](https://star-history.com/#julienwuthrich/cookiecutter-fastapi-nextjs-llm&Date)

---

## 📄 **License**

This template is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **[Agno](https://docs.agno.com)** - Powerful AI agent framework
- **[OpenRouter](https://openrouter.ai)** - Unified model access
- **[Cookiecutter](https://cookiecutter.readthedocs.io/)** - Project templating
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Next.js](https://nextjs.org)** - React framework for production
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package manager

---

<div align="center">

## 🚀 **Ready to Build Your AI Agent App?**

```bash
cookiecutter https://github.com/julienwuthrich/cookiecutter-fastapi-nextjs-llm
```

**Generate. Code. Deploy. Scale.** 🎯

[Get Started](https://github.com/julienwuthrich/cookiecutter-fastapi-nextjs-llm) • [View Examples](https://github.com/julienwuthrich/cookiecutter-fastapi-nextjs-llm/wiki) • [Issues](https://github.com/julienwuthrich/cookiecutter-fastapi-nextjs-llm/issues)

</div>
