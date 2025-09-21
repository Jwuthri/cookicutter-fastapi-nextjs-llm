# Backend Dockerfile for {{cookiecutter.project_name}}
FROM python:{{cookiecutter.python_version}}-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1

# Install system dependencies including curl for uv installation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv .venv
ENV VIRTUAL_ENV=.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies using uv
RUN uv pip install -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{{cookiecutter.backend_port}}/health || exit 1

# Expose port
EXPOSE {{cookiecutter.backend_port}}

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{{cookiecutter.backend_port}}"]
