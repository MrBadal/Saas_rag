from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Determine the project root directory (parent of backend/)
# This file is at: backend/app/core/config.py
# Project root is: backend/app/core/../../../
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://raguser:ragpass@localhost:5432/ragdb"
    
    # Local Models Configuration
    USE_LOCAL_MODELS: bool = True
    EMBEDDING_SERVICE_URL: str = "http://localhost:8001"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # OpenAI (optional - only if USE_LOCAL_MODELS=false)
    OPENAI_API_KEY: Optional[str] = None
    
    # AWS (optional for deployment)
    AWS_REGION: Optional[str] = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    class Config:
        env_file = "../../.env"
        case_sensitive = True

settings = Settings()
