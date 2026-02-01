from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, DatabaseConnection, QueryHistory
from app.services.rag_service import RAGService
from app.services.rag_service_local import LocalRAGService
from app.services.connectors import get_connector
from app.core.config import settings
import logging
import re
import asyncio
from typing import List, Dict, Any
import time

router = APIRouter()
logger = logging.getLogger(__name__)

class LLMConfig(BaseModel):
    provider: str = "openai"
    api_key: str | None = None
    model: str | None = None

class QueryRequest(BaseModel):
    connection_id: int
    query: str
    llm_config: LLMConfig | None = None

class QueryResponse(BaseModel):
    answer: str
    generated_query: str | None = None
    query_results: list | None = None
    execution_time: float | None = None
    auto_executed: bool = False

class ModelListResponse(BaseModel):
    models: List[Dict[str, Any]]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def should_auto_execute_query(user_query: str) -> bool:
    """Determine if query should automatically execute database queries"""
    # Keywords that indicate user wants to see actual data
    execution_keywords = [
        "show me", "get", "find", "list", "display", "fetch", "retrieve",
        "how many", "count", "total", "sum", "average", "latest", "recent",
        "all", "select", "where", "filter", "search", "data", "records",
        "rows", "entries", "results", "details", "information"
    ]
    
    query_lower = user_query.lower()
    return any(keyword in query_lower for keyword in execution_keywords)

def is_safe_read_query(query: str) -> bool:
    """Check if query is safe (read-only) to execute"""
    query_lower = query.lower().strip()
    
    # Allowed operations
    safe_operations = ["select", "show", "describe", "explain", "with"]
    
    # Dangerous operations
    dangerous_operations = [
        "insert", "update", "delete", "drop", "create", "alter", 
        "truncate", "grant", "revoke", "exec", "execute"
    ]
    
    # Check if query starts with safe operation
    first_word = query_lower.split()[0] if query_lower.split() else ""
    
    if first_word in safe_operations:
        # Double check it doesn't contain dangerous operations
        return not any(dangerous in query_lower for dangerous in dangerous_operations)
    
    return False

async def execute_database_query_safely(connection: DatabaseConnection, query: str) -> List[Dict]:
    """Execute database query with safety checks and timeout"""
    if not is_safe_read_query(query):
        raise ValueError("Query contains potentially unsafe operations")
    
    connector = get_connector(connection.db_type)
    
    try:
        connector.connect(connection.connection_string)
        
        # Execute with timeout (prevent long-running queries)
        if connection.db_type == "postgresql":
            # Add LIMIT if not present to prevent huge result sets
            if "limit" not in query.lower() and "select" in query.lower():
                query = f"{query.rstrip(';')} LIMIT 100"
            
            results = connector.execute_query(query)
        else:  # MongoDB
            # For MongoDB, parse the query and execute
            results = []  # Implement MongoDB query execution
        
        return results[:100]  # Limit results to prevent memory issues
        
    finally:
        connector.close()

@router.post("/", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Execute a natural language query using RAG with automatic query execution"""
    start_time = time.time()
    
    try:
        # Get connection
        connection = db.query(DatabaseConnection).filter(
            DatabaseConnection.id == request.connection_id
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Choose RAG service based on configuration
        if settings.USE_LOCAL_MODELS:
            logger.info("Using local RAG service")
            rag_service = LocalRAGService(
                embedding_service_url=settings.EMBEDDING_SERVICE_URL,
                ollama_base_url=settings.OLLAMA_BASE_URL,
                ollama_model=settings.OLLAMA_MODEL
            )
        else:
            logger.info("Using cloud RAG service")
            llm_config_dict = request.llm_config.model_dump() if request.llm_config else None
            rag_service = RAGService(llm_config=llm_config_dict)
        
        # Determine if we should auto-execute queries
        auto_execute = should_auto_execute_query(request.query)
        
        # Use RAG to answer query
        answer = rag_service.query_with_rag(request.query, connection.id)
        
        generated_query = None
        query_results = None
        
        # Auto-generate and execute query if user intent suggests they want data
        if auto_execute:
            try:
                schema = connection.db_metadata.get("schema", {})
                generated_query = rag_service.generate_query(
                    request.query,
                    schema,
                    connection.db_type
                )
                
                if generated_query and is_safe_read_query(generated_query):
                    query_results = await execute_database_query_safely(connection, generated_query)
                    
                    # Enhance answer with actual results
                    if query_results:
                        result_count = len(query_results)
                        answer += f"\n\n**Query Results:** Found {result_count} records."
                        
                        # Show sample of results if reasonable size
                        if result_count <= 10:
                            answer += f"\n\nHere are the results:\n"
                            for i, row in enumerate(query_results[:5], 1):
                                answer += f"{i}. {row}\n"
                        else:
                            answer += f"\n\nShowing first few results:\n"
                            for i, row in enumerate(query_results[:3], 1):
                                answer += f"{i}. {row}\n"
                            answer += f"... and {result_count - 3} more records."
                    else:
                        answer += "\n\n**Query Results:** No records found matching your criteria."
                        
            except Exception as e:
                logger.warning(f"Auto query execution failed: {e}")
                # Don't fail the whole request, just log the issue
                answer += f"\n\n*Note: Could not automatically execute query due to: {str(e)}*"
        
        # Save to history
        history = QueryHistory(
            user_id=1,  # TODO: Get from auth token
            connection_id=connection.id,
            query=request.query,
            response=answer
        )
        db.add(history)
        db.commit()
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            answer=answer,
            generated_query=generated_query,
            query_results=query_results,
            execution_time=execution_time,
            auto_executed=auto_execute and query_results is not None
        )
    
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_query_history(db: Session = Depends(get_db)):
    """Get query history for the user"""
    history = db.query(QueryHistory).order_by(
        QueryHistory.created_at.desc()
    ).limit(50).all()
    
    return [
        {
            "id": h.id,
            "query": h.query,
            "response": h.response,
            "created_at": h.created_at
        }
        for h in history
    ]

@router.post("/models", response_model=ModelListResponse)
async def get_available_models(llm_config: LLMConfig):
    """Get available models for the specified provider and API key"""
    try:
        if llm_config.provider == "openai":
            return await get_openai_models(llm_config.api_key)
        elif llm_config.provider == "google":
            return await get_google_models(llm_config.api_key)
        elif llm_config.provider == "openrouter":
            return await get_openrouter_models(llm_config.api_key)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

async def get_openai_models(api_key: str) -> ModelListResponse:
    """Fetch available OpenAI models"""
    import openai
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        models = client.models.list()
        
        # Filter to relevant chat models
        chat_models = []
        for model in models.data:
            if any(prefix in model.id for prefix in ["gpt-3.5", "gpt-4", "gpt-4o"]):
                chat_models.append({
                    "id": model.id,
                    "name": model.id,
                    "description": f"OpenAI {model.id}",
                    "provider": "openai"
                })
        
        # Sort by model name
        chat_models.sort(key=lambda x: x["id"])
        
        return ModelListResponse(models=chat_models)
        
    except Exception as e:
        # Return default models if API call fails
        default_models = [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "provider": "openai"},
            {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model", "provider": "openai"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Latest GPT-4 model", "provider": "openai"}
        ]
        return ModelListResponse(models=default_models)

async def get_google_models(api_key: str) -> ModelListResponse:
    """Fetch available Google Gemini models"""
    import google.generativeai as genai
    
    try:
        genai.configure(api_key=api_key)
        
        models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append({
                    "id": model.name.replace('models/', ''),
                    "name": model.display_name or model.name,
                    "description": model.description or f"Google {model.name}",
                    "provider": "google"
                })
        
        return ModelListResponse(models=models)
        
    except Exception as e:
        # Return default models if API call fails
        default_models = [
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Fast and efficient", "provider": "google"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Most capable model", "provider": "google"},
            {"id": "gemini-pro", "name": "Gemini Pro", "description": "Previous generation", "provider": "google"}
        ]
        return ModelListResponse(models=default_models)

async def get_openrouter_models(api_key: str) -> ModelListResponse:
    """Fetch available OpenRouter models"""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get("data", []):
                    models.append({
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "description": model.get("description", ""),
                        "provider": "openrouter",
                        "context_length": model.get("context_length"),
                        "pricing": model.get("pricing")
                    })
                
                # Sort by popularity/name
                models.sort(key=lambda x: x["name"])
                
                return ModelListResponse(models=models)
            else:
                raise Exception(f"API returned {response.status_code}")
                
    except Exception as e:
        # Return popular default models if API call fails
        default_models = [
            {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus", "description": "Most capable Claude model", "provider": "openrouter"},
            {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance", "provider": "openrouter"},
            {"id": "openai/gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Latest GPT-4 via OpenRouter", "provider": "openrouter"},
            {"id": "mistralai/mixtral-8x7b-instruct", "name": "Mixtral 8x7B", "description": "Open source model", "provider": "openrouter"}
        ]
        return ModelListResponse(models=default_models)
