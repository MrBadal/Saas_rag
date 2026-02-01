@echo off
echo 🚀 Setting up Self-Hosted RAG System
echo ====================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created. Please update it with your settings.
)

REM Build and start services
echo.
echo 🏗️  Building Docker images...
docker-compose build

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Pull Ollama model
echo.
echo 📥 Downloading Ollama model (llama3.2)...
echo This may take a few minutes on first run...
docker exec ollama ollama pull llama3.2

echo.
echo ✅ Setup complete!
echo.
echo 📊 Service Status:
docker-compose ps

echo.
echo 🌐 Access your application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Embedding Service: http://localhost:8001
echo    Ollama: http://localhost:11434
echo.
echo 📝 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo.
pause
