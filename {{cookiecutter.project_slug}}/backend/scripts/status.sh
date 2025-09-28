#!/bin/bash
# Status script for {{cookiecutter.project_name}} Backend

set -e

echo "📊 {{cookiecutter.project_name}} Backend Status"
echo "=============================================="

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local path=${3:-"/health"}
    local protocol=${4:-"http"}

    echo -n "🔍 $service_name: "

    if curl -f -s "${protocol}://localhost:${port}${path}" > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy or not running"
    fi
}

# Function to check Docker container status
check_container() {
    local container_name=$1
    local display_name=${2:-$container_name}

    echo -n "🐳 $display_name: "

    if docker ps --format "table {{ '{{.Names}}' }}" | grep -q "$container_name"; then
        status=$(docker inspect --format='{{ '{{.State.Status}}' }}' "$container_name" 2>/dev/null || echo "not found")
        if [ "$status" = "running" ]; then
            echo "✅ Running"
        else
            echo "⚠️  $status"
        fi
    else
        echo "❌ Not running"
    fi
}

echo ""
echo "🐳 Docker Containers:"
echo "--------------------"

# Check development containers
if docker ps -a --format "table {{ '{{.Names}}' }}" | grep -q "{{cookiecutter.project_slug}}.*_dev"; then
    echo "Development Environment:"
    check_container "{{cookiecutter.project_slug}}_backend_dev" "Backend (Dev)"
    {% if cookiecutter.include_database == "postgresql" %}
    check_container "{{cookiecutter.project_slug}}_postgres_dev" "PostgreSQL (Dev)"
    {% endif %}
    check_container "{{cookiecutter.project_slug}}_redis_dev" "Redis (Dev)"
    check_container "{{cookiecutter.project_slug}}_kafka_dev" "Kafka (Dev)"
    check_container "{{cookiecutter.project_slug}}_zookeeper_dev" "Zookeeper (Dev)"
    check_container "{{cookiecutter.project_slug}}_rabbitmq_dev" "RabbitMQ (Dev)"
    echo ""
fi

# Check production containers
if docker ps -a --format "table {{ '{{.Names}}' }}" | grep -q "{{cookiecutter.project_slug}}_.*" | grep -v "_dev"; then
    echo "Production Environment:"
    check_container "{{cookiecutter.project_slug}}_backend" "Backend (Prod)"
    {% if cookiecutter.include_database == "postgresql" %}
    check_container "{{cookiecutter.project_slug}}_postgres" "PostgreSQL (Prod)"
    {% endif %}
    check_container "{{cookiecutter.project_slug}}_redis" "Redis (Prod)"
    check_container "{{cookiecutter.project_slug}}_kafka" "Kafka (Prod)"
    check_container "{{cookiecutter.project_slug}}_zookeeper" "Zookeeper (Prod)"
    check_container "{{cookiecutter.project_slug}}_rabbitmq" "RabbitMQ (Prod)"
    echo ""
fi

echo "🌐 Service Health Checks:"
echo "------------------------"

# Check service endpoints
check_service "Backend API" "{{cookiecutter.backend_port}}" "/health"
check_service "Backend Docs" "{{cookiecutter.backend_port}}" "/docs"
{% if cookiecutter.include_database == "postgresql" %}

# PostgreSQL health check
echo -n "🔍 PostgreSQL: "
if docker exec {{cookiecutter.project_slug}}_postgres_dev pg_isready -U postgres > /dev/null 2>&1 || \
   docker exec {{cookiecutter.project_slug}}_postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi
{% endif %}

# Redis health check
echo -n "🔍 Redis: "
if docker exec {{cookiecutter.project_slug}}_redis_dev redis-cli ping > /dev/null 2>&1 || \
   docker exec {{cookiecutter.project_slug}}_redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi

# RabbitMQ health check
echo -n "🔍 RabbitMQ: "
if curl -f -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✅ Healthy (Management UI available)"
else
    echo "❌ Unhealthy or not running"
fi

# Kafka health check
echo -n "🔍 Kafka: "
if docker exec {{cookiecutter.project_slug}}_kafka_dev kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1 || \
   docker exec {{cookiecutter.project_slug}}_kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi

echo ""
echo "📈 Resource Usage:"
echo "-----------------"

# Show Docker stats for running containers
if docker ps --format "table {{ '{{.Names}}' }}" | grep -q "{{cookiecutter.project_slug}}"; then
    echo "Docker Container Stats:"
    docker stats --no-stream --format "table {{ '{{.Name}}' }}\t{{ '{{.CPUPerc}}' }}\t{{ '{{.MemUsage}}' }}" $(docker ps --filter "name={{cookiecutter.project_slug}}" --format "{{ '{{.Names}}' }}" | tr '\n' ' ') 2>/dev/null || true
else
    echo "No {{cookiecutter.project_name}} containers running."
fi

echo ""
echo "🔗 Quick Links:"
echo "--------------"
echo "📋 Backend API: http://localhost:{{cookiecutter.backend_port}}"
echo "📚 API Documentation: http://localhost:{{cookiecutter.backend_port}}/docs"
echo "🩺 Health Check: http://localhost:{{cookiecutter.backend_port}}/health"
{% if cookiecutter.include_database == "postgresql" %}
echo "🗄️ pgAdmin: http://localhost:5050 (admin@{{cookiecutter.project_slug}}.local / admin)"
{% endif %}
echo "🐰 RabbitMQ Management: http://localhost:15672 (guest/guest)"

# Show optional UIs if they're running
if docker ps --format "table {{ '{{.Names}}' }}" | grep -q "kafka_ui"; then
    echo "📊 Kafka UI: http://localhost:8080"
fi

if docker ps --format "table {{ '{{.Names}}' }}" | grep -q "redis_commander"; then
    echo "📊 Redis Commander: http://localhost:8081"
fi

echo ""
echo "💡 Tips:"
echo "   • Run './scripts/start.sh' to start services"
echo "   • Run './scripts/stop.sh' to stop services"
echo "   • Run 'docker-compose logs -f <service>' to view logs"
