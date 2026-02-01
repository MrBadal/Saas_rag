@echo off
echo Starting Universal RAG Platform...

REM Check if .env exists
if not exist .env (
    echo .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env and add your OPENAI_API_KEY
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker first.
    exit /b 1
)

echo Starting Docker containers...
docker-compose up -d

echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo Initializing database...
docker-compose exec -T backend python -c "from app.models.database import init_db; init_db()"

echo.
echo Platform is ready!
echo.
echo Access points:
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo Next steps:
echo    1. Open http://localhost:3000
echo    2. Register a new account
echo    3. Add a database connection
echo    4. Start querying with AI!
echo.
echo To stop: docker-compose down
