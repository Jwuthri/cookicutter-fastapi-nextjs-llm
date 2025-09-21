# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## 🚀 Features

- **FastAPI Backend**: High-performance Python API with auto-generated docs
- **Next.js Frontend**: Modern React application with App Router
- **Real-time Chat**: {% if cookiecutter.use_websockets == "yes" %}WebSocket-powered{% else %}HTTP-based{% endif %} messaging
- **LLM Integration**: {{cookiecutter.llm_provider}} for AI-powered conversations
- **Redis Caching**: Fast response times with intelligent caching
- **Message Queuing**: Kafka & RabbitMQ for scalable event processing
- **Database Support**: {% if cookiecutter.include_database == "postgresql" %}PostgreSQL{% elif cookiecutter.include_database == "sqlite" %}SQLite{% else %}In-memory storage{% endif %} for data persistence
- **Docker Ready**: Complete containerization with Docker Compose
- **Production Ready**: Comprehensive monitoring and error handling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │───▶│  FastAPI API    │───▶│   LLM Service   │
│    (Frontend)  │    │   (Backend)     │    │ ({{cookiecutter.llm_provider}}) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │     Redis       │
         │              │   (Caching)     │
         │              └─────────────────┘
         │
         ▼              ┌─────────────────┐    ┌─────────────────┐
┌─────────────────┐    │     Kafka       │    │   RabbitMQ      │
│   WebSocket     │    │  (Streaming)    │    │  (Queuing)      │
│  (Real-time)    │    └─────────────────┘    └─────────────────┘
└─────────────────┘
{% if cookiecutter.include_database != "none" %}
         │              ┌─────────────────┐
         │              │  {{cookiecutter.include_database | title}}  │
         └─────────────▶│   Database      │
                        └─────────────────┘
{% endif %}
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **uvicorn/Gunicorn** - ASGI servers for production
- **uv** - Ultra-fast Python package manager
- **Redis** - Caching and session management
- **Kafka** - Event streaming platform
- **RabbitMQ** - Message broker for reliable queuing
{% if cookiecutter.include_database != "none" %}- **{{cookiecutter.include_database | title}}** - Database for persistent storage{% endif %}
- **{{cookiecutter.llm_provider | title}}** - LLM provider for AI responses

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Markdown** - Markdown rendering for chat messages
{% if cookiecutter.use_websockets == "yes" %}- **WebSocket** - Real-time communication{% endif %}

## 🚀 Quick Start

### Prerequisites

- **Python {{cookiecutter.python_version}}+**
- **Node.js {{cookiecutter.node_version}}+**
- **Docker & Docker Compose**

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd {{cookiecutter.project_slug}}

# Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

The application will be available at:
- **Frontend**: http://localhost:{{cookiecutter.frontend_port}}
- **Backend API**: http://localhost:{{cookiecutter.backend_port}}
- **API Docs**: http://localhost:{{cookiecutter.backend_port}}/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Start Redis, Kafka, RabbitMQ with Docker
docker-compose up redis kafka rabbitmq{% if cookiecutter.include_database == "postgresql" %} postgres{% endif %} -d

# Run the backend
uvicorn app.main:app --host 0.0.0.0 --port {{cookiecutter.backend_port}} --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Configuration

### Backend Environment Variables

```env
# LLM Configuration
{% if cookiecutter.llm_provider == "openai" %}OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
{% elif cookiecutter.llm_provider == "anthropic" %}ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
{% endif %}

# Database Configuration
{% if cookiecutter.include_database == "postgresql" %}DATABASE_URL=postgresql://postgres:postgres@localhost:{{cookiecutter.postgres_port}}/{{cookiecutter.project_slug}}
{% elif cookiecutter.include_database == "sqlite" %}DATABASE_URL=sqlite:///./data/{{cookiecutter.project_slug}}.db
{% endif %}

# Service URLs
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:{{cookiecutter.backend_port}}
{% if cookiecutter.use_websockets == "yes" %}NEXT_PUBLIC_WS_URL=ws://localhost:{{cookiecutter.backend_port}}
{% endif %}NEXT_PUBLIC_APP_NAME={{cookiecutter.project_name}}
```

## 📊 Monitoring & Health Checks

- **Backend Health**: `GET /health`
- **Frontend Health**: `GET /api/health`
- **API Documentation**: `/docs` (Swagger UI) and `/redoc`

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
uv run ruff check .
uv run black .
uv run mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:{{cookiecutter.backend_port}}/docs
- **ReDoc**: http://localhost:{{cookiecutter.backend_port}}/redoc

### Key Endpoints

- `POST /api/chat` - Send a chat message
- `GET /api/chat/sessions/{session_id}` - Get chat history
- `DELETE /api/chat/sessions/{session_id}` - Delete a session
{% if cookiecutter.use_websockets == "yes" %}- `WS /ws/{session_id}` - WebSocket connection{% endif %}

## 🔀 Message Flow

1. **User Message**: Frontend → Backend API
2. **Processing**: Backend → Redis (cache check) → LLM Service
3. **Events**: Kafka (analytics) + RabbitMQ (task queue)
4. **Response**: Backend → Frontend{% if cookiecutter.use_websockets == "yes" %} (+ WebSocket broadcast){% endif %}

## 🚀 Production Deployment

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy with reverse proxy
docker-compose --profile production up -d
```

### Manual Deployment

1. **Backend**: Deploy with Gunicorn + Nginx
2. **Frontend**: Build static files with `npm run build`
3. **Services**: Set up Redis, Kafka, RabbitMQ clusters
4. **Database**: Configure {% if cookiecutter.include_database != "none" %}{{cookiecutter.include_database}}{% else %}your preferred database{% endif %} with connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**{{cookiecutter.author_name}}**  
Email: {{cookiecutter.author_email}}

---

Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com/) and [Next.js](https://nextjs.org/)
