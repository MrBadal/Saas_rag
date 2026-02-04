@echo off
REM LLM Configuration Helper Script for Windows
REM This script helps you configure the DataQuery AI system for optimal performance

echo ==========================================
echo DataQuery AI - LLM Configuration Helper
echo ==========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

echo How would you like to configure your LLM?
echo.
echo 1) Cloud LLMs (Recommended - Fast, No memory issues)
echo 2) Local Models (Ollama - Privacy-focused, requires RAM)
echo 3) Show current configuration
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto cloud
if "%choice%"=="2" goto local
if "%choice%"=="3" goto show
goto invalid

:cloud
echo.
echo Configuring for Cloud LLMs...
echo.

REM Update .env to disable local models
powershell -Command "(Get-Content .env) -replace 'USE_LOCAL_MODELS=.*', 'USE_LOCAL_MODELS=false' | Set-Content .env"

echo [OK] Cloud LLM mode enabled
echo.
echo Next steps:
echo 1. Start the application: start.bat
echo 2. Open http://localhost:3000
echo 3. Click 'LLM Settings' in the UI
echo 4. Select your provider (OpenAI/Google/OpenRouter)
echo 5. Enter your API key
echo 6. Select a model and save
echo.
echo Get API keys from:
echo - OpenAI: https://platform.openai.com/api-keys
echo - Google Gemini: https://makersuite.google.com/app/apikey
echo - OpenRouter: https://openrouter.ai/keys
goto end

:local
echo.
echo Configuring for Local Models (Ollama)...
echo.

echo Available models:
echo 1) llama3.2:1b (1.3GB RAM) - Fastest, lowest memory
echo 2) llama3.2 (2.0GB RAM) - Balanced
echo 3) llama3.2:3b (2.3GB RAM) - Better quality
echo 4) mistral (4.1GB RAM) - High quality
echo.
set /p model_choice="Enter choice (1-4): "

if "%model_choice%"=="1" set model=llama3.2:1b
if "%model_choice%"=="2" set model=llama3.2
if "%model_choice%"=="3" set model=llama3.2:3b
if "%model_choice%"=="4" set model=mistral
if "%model%"=="" set model=llama3.2:1b

echo.
echo Pulling Ollama model: %model%
ollama pull %model%

if %errorlevel% equ 0 (
    echo [OK] Model downloaded successfully
    
    REM Update .env
    powershell -Command "(Get-Content .env) -replace 'USE_LOCAL_MODELS=.*', 'USE_LOCAL_MODELS=true' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'OLLAMA_MODEL=.*', 'OLLAMA_MODEL=%model%' | Set-Content .env"
    
    echo [OK] Configuration updated
    echo.
    echo Next steps:
    echo 1. Start the application: start.bat
    echo 2. Open http://localhost:3000
    echo 3. Start chatting!
) else (
    echo [ERROR] Failed to download model
    echo Please ensure Ollama is installed and running
    echo Install from: https://ollama.ai
)
goto end

:show
echo.
echo Current Configuration:
echo =====================
if exist ".env" (
    echo.
    findstr "USE_LOCAL_MODELS" .env
    findstr "OLLAMA_MODEL" .env
    echo.
    
    findstr "USE_LOCAL_MODELS=true" .env >nul
    if %errorlevel% equ 0 (
        echo Mode: Local Models (Ollama)
        echo.
        echo Check Ollama status:
        ollama list
    ) else (
        echo Mode: Cloud LLMs
        echo Configure API keys in the UI (LLM Settings)
    )
) else (
    echo .env file not found
)
goto end

:invalid
echo Invalid choice
exit /b 1

:end
echo.
echo ==========================================
echo Configuration complete!
echo ==========================================
pause