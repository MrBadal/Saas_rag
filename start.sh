#!/bin/bash

echo "🚀 Starting Universal RAG Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 5

echo "🗄️  Initializing database..."
docker-compose exec -T backend python -c "from app.models.database import init_db; init_db()"

echo ""
echo "✅ Platform is ready!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📖 Next steps:"
echo "   1. Open http://localhost:3000"
echo "   2. Register a new account"
echo "   3. Add a database connection"
echo "   4. Start querying with AI!"
echo ""
echo "🛑 To stop: docker-compose down"
