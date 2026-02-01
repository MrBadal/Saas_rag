from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, UserSettings
from typing import Optional, List, Dict
import requests

router = APIRouter()

class SettingsUpdate(BaseModel):
    llm_provider: str
    llm_api_key: str
    llm_model: Optional[str] = None

class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    has_api_key: bool
    key_last_updated: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_openrouter_models(api_key: str = None) -> List[Dict]:
    """Fetch available models from OpenRouter"""
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get("data", []):
                models.append({
                    "id": model["id"],
                    "name": model.get("name", model["id"]),
                    "description": model.get("description", ""),
                    "context_length": model.get("context_length", 0),
                    "pricing": model.get("pricing", {})
                })
            return models
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
    
    # Fallback to common models if API call fails
    return [
        {"id": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"},
        {"id": "openai/gpt-4", "name": "GPT-4", "description": "Most capable"},
        {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus", "description": "Excellent reasoning"},
        {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced"},
        {"id": "google/gemini-pro", "name": "Gemini Pro", "description": "Google's model"},
        {"id": "meta-llama/llama-2-70b-chat", "name": "Llama 2 70B", "description": "Open source"},
    ]

def test_api_key(provider: str, api_key: str, model: str = None) -> Dict:
    """Test if an API key is valid by making a simple request"""
    try:
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            # Make a simple completion request
            response = client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return {"valid": True, "message": "API key is valid"}
        
        elif provider == "openrouter":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model or "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            if response.status_code == 200:
                return {"valid": True, "message": "API key is valid"}
            else:
                return {"valid": False, "message": response.json().get("error", {}).get("message", "Invalid API key")}
        
        elif provider == "gemini":
            # Gemini API key testing
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model or "gemini-pro")
            response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
            return {"valid": True, "message": "API key is valid"}
        
        elif provider == "anthropic":
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": model or "claude-3-haiku-20240307",
                    "max_tokens": 5,
                    "messages": [{"role": "user", "content": "Hi"}]
                },
                timeout=10
            )
            if response.status_code == 200:
                return {"valid": True, "message": "API key is valid"}
            else:
                return {"valid": False, "message": "Invalid API key"}
        
        return {"valid": False, "message": "Provider not supported for testing"}
    
    except Exception as e:
        return {"valid": False, "message": str(e)}

@router.get("/", response_model=SettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Get user settings (without API key)"""
    # TODO: Get actual user_id from auth token
    user_id = 1
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        # Create default settings
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SettingsResponse(
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        has_api_key=bool(settings.llm_api_key),
        key_last_updated=settings.updated_at.isoformat() if settings.updated_at else None
    )

@router.post("/")
async def update_settings(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    """Update user settings including API key"""
    # TODO: Get actual user_id from auth token
    user_id = 1
    
    # Test the API key before saving
    if settings_update.llm_api_key:
        test_result = test_api_key(
            settings_update.llm_provider,
            settings_update.llm_api_key,
            settings_update.llm_model
        )
        if not test_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"API key validation failed: {test_result['message']}"
            )
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
    
    settings.llm_provider = settings_update.llm_provider
    settings.llm_api_key = settings_update.llm_api_key
    if settings_update.llm_model:
        settings.llm_model = settings_update.llm_model
    
    db.commit()
    
    return {
        "message": "Settings saved successfully",
        "provider": settings_update.llm_provider,
        "model": settings_update.llm_model,
        "key_valid": True
    }

@router.post("/test-key")
async def test_settings_key(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    """Test an API key without saving it"""
    if not settings_update.llm_api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    test_result = test_api_key(
        settings_update.llm_provider,
        settings_update.llm_api_key,
        settings_update.llm_model
    )
    
    return test_result

@router.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers and their models"""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": [
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and cost-effective"},
                    {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
                    {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo", "description": "Latest GPT-4 with 128k context"}
                ],
                "key_url": "https://platform.openai.com/account/api-keys",
                "description": "Industry-leading AI models by OpenAI"
            },
            {
                "id": "openrouter",
                "name": "OpenRouter",
                "models": [
                    {"id": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo via OpenRouter", "description": "Access GPT-3.5 through OpenRouter"},
                    {"id": "openai/gpt-4", "name": "GPT-4 via OpenRouter", "description": "Access GPT-4 through OpenRouter"},
                    {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus", "description": "Most capable Claude model"},
                    {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance and speed"},
                    {"id": "google/gemini-pro", "name": "Gemini Pro", "description": "Google's multimodal model"},
                    {"id": "meta-llama/llama-2-70b-chat", "name": "Llama 2 70B", "description": "Open source model by Meta"}
                ],
                "key_url": "https://openrouter.ai/keys",
                "description": "Unified API for multiple AI models. One key, many models.",
                "supports_custom_models": True
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "models": [
                    {"id": "gemini-pro", "name": "Gemini Pro", "description": "Multimodal model by Google"},
                    {"id": "gemini-ultra", "name": "Gemini Ultra", "description": "Most capable Gemini model"}
                ],
                "key_url": "https://makersuite.google.com/app/apikey",
                "description": "Google's AI models with large context windows"
            },
            {
                "id": "anthropic",
                "name": "Anthropic Claude",
                "models": [
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Most capable Claude model"},
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "description": "Balanced performance"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "description": "Fast and efficient"}
                ],
                "key_url": "https://console.anthropic.com/settings/keys",
                "description": "AI models focused on safety and helpfulness"
            }
        ]
    }

@router.get("/openrouter-models")
async def get_openrouter_available_models(api_key: str = None):
    """Get real-time list of OpenRouter models"""
    models = get_openrouter_models(api_key)
    return {"models": models}
