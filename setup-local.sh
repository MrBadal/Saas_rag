#!/bin/bash

echo "🚀 Setting up Self-Hosted RAG System"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please update it with your settings."
fi

# Build and start services
echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Pull Ollama model
echo ""
echo "📥 Downloading Ollama model (llama3.2)..."
echo "This may take a few minutes on first run..."
docker exec ollama ollama pull llama3.2

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Embedding Service: http://localhost:8001"
echo "   Ollama: http://localhost:11434"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
