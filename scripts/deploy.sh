#!/bin/bash

# Deployment script for EC2 instance
# This script is called by GitHub Actions to deploy the application

set -e

echo "=========================================="
echo "SaaS RAG Application Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as ubuntu user (not root)
if [ "$EUID" -eq 0 ]; then
   print_error "Please run as ubuntu user, not root"
   exit 1
fi

# Navigate to app directory
APP_DIR="$HOME/SaaS_rag"
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found at $APP_DIR"
    print_status "Please clone the repository first:"
    print_status "git clone <your-repo-url> $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Pull latest code
print_status "Pulling latest code from repository..."
git fetch origin
git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)

# Check if .env file exists, create from example if not
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from .env.example"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env file with your actual values before next deployment"
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Pull latest images (if using pre-built images)
print_status "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull || true

# Build containers
print_status "Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start containers
print_status "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start (30 seconds)..."
sleep 30

# Check service health
print_status "Checking service health..."
echo ""
echo "Container Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "Checking individual services..."

# Check PostgreSQL
if docker exec ragdb pg_isready -U raguser > /dev/null 2>&1; then
    print_status "PostgreSQL is running"
else
    print_warning "PostgreSQL may still be starting..."
fi

# Check Backend
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    print_status "Backend API is accessible"
else
    print_warning "Backend API may still be starting..."
fi

# Check Embedding Service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    print_status "Embedding Service is running"
else
    print_warning "Embedding Service may still be starting..."
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama is running"
    
    # Check if model is pulled
    if curl -s http://localhost:11434/api/tags | grep -q "llama3.2:1b"; then
        print_status "LLM model (llama3.2:1b) is available"
    else
        print_warning "LLM model not found. Pulling llama3.2:1b (this may take 2-3 minutes)..."
        docker exec ollama ollama pull llama3.2:1b || print_warning "Model pull failed, will retry on next deployment"
    fi
else
    print_warning "Ollama may still be starting..."
fi

# Clean up old images
print_status "Cleaning up old Docker images..."
docker image prune -f

# Show resource usage
echo ""
print_status "Container Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "=========================================="
print_status "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Access your application at:"
echo "  Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "  Backend API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo ""
echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "To stop: docker-compose -f docker-compose.prod.yml down"
echo "=========================================="