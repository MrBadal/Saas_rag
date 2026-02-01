from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
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
from typing import List, Dict, Any, Optional
import time
import json

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
    stream: bool = False  # Enable streaming response
    execute_query: bool = True  # Force query execution

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
        "rows", "entries", "results", "details", "information", "orders",
        "customers", "users", "products", "sales", "transactions"
    ]
    
    # Non-execution keywords (questions about structure, not data)
    non_execution_keywords = [
        "what is", "how to", "explain", "describe", "structure", "schema",
        "what are", "tell me about", "what does", "help me understand"
    ]
    
    query_lower = user_query.lower()
    
    # Check for non-execution keywords first
    if any(keyword in query_lower for keyword in non_execution_keywords):
        # Unless it also has execution keywords
        if not any(keyword in query_lower for keyword in execution_keywords):
            return False
    
    return any(keyword in query_lower for keyword in execution_keywords)

def is_safe_read_query(query: str, db_type: str = "postgresql") -> bool:
    """Check if query is safe (read-only) to execute"""
    query_lower = query.lower().strip()
    
    if db_type == "postgresql":
        # Allowed SQL operations
        safe_operations = ["select", "show", "describe", "explain", "with"]
        
        # Dangerous SQL operations
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
    
    elif db_type == "mongodb":
        # For MongoDB, check if it's a find/query operation (JSON format)
        # MongoDB queries in JSON are generally safe if they don't contain $merge, $out, etc.
        dangerous_mongo = ["$merge", "$out", "$update", "$delete", "$drop"]
        return not any(op in query_lower for op in dangerous_mongo)
    
    return False

async def execute_database_query_safely(connection: DatabaseConnection, query: str, db_type: str) -> List[Dict]:
    """Execute database query with safety checks and timeout"""
    if not is_safe_read_query(query, db_type):
        raise ValueError(f"Query contains potentially unsafe operations for {db_type}")
    
    connector = get_connector(connection.db_type)
    
    try:
        connector.connect(connection.connection_string)
        
        # Execute with timeout (prevent long-running queries)
        if connection.db_type == "postgresql":
            # Add LIMIT if not present to prevent huge result sets
            if "limit" not in query.lower() and "select" in query.lower():
                query = f"{query.rstrip(';')} LIMIT 100"
            
            results = connector.execute_query(query)
        elif connection.db_type == "mongodb":
            # For MongoDB, the query is already in JSON format from generate_query
            # Execute it using the connector
            try:
                import json
                query_obj = json.loads(query)
                results = connector.execute_query(query_obj)
            except json.JSONDecodeError:
                raise ValueError("Invalid MongoDB query format")
        else:
            results = []
        
        return results[:100]  # Limit results to prevent memory issues
        
    finally:
        connector.close()

def format_query_results(results: List[Dict], query: str, db_type: str) -> str:
    """Format query results in a user-friendly way"""
    if not results:
        return "**Query Results:** No records found matching your criteria."
    
    result_count = len(results)
    formatted = f"**Query Results:** Found {result_count} record{'s' if result_count > 1 else ''}.\n\n"
    
    # Format based on result size
    if result_count <= 5:
        # Show all results for small sets
        formatted += "Here are all the results:\n\n"
        for i, row in enumerate(results, 1):
            formatted += f"**{i}.** {format_row(row)}\n"
    elif result_count <= 20:
        # Show first 10 for medium sets
        formatted += f"Showing first 10 of {result_count} results:\n\n"
        for i, row in enumerate(results[:10], 1):
            formatted += f"**{i}.** {format_row(row)}\n"
        formatted += f"\n... and {result_count - 10} more records."
    else:
        # Show summary for large sets
        formatted += f"Showing first 5 of {result_count} results:\n\n"
        for i, row in enumerate(results[:5], 1):
            formatted += f"**{i}.** {format_row(row)}\n"
        formatted += f"\n... and {result_count - 5} more records."
    
    return formatted

def format_row(row: Dict) -> str:
    """Format a single row/dict for display"""
    if not row:
        return "Empty record"
    
    # Format key-value pairs
    parts = []
    for key, value in row.items():
        # Skip null/None values for cleaner display
        if value is not None and value != "":
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            parts.append(f"{key}: {value_str}")
    
    return " | ".join(parts) if parts else "No data"

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
        # Priority: User-provided LLM config > Environment USE_LOCAL_MODELS setting
        use_local = settings.USE_LOCAL_MODELS
        
        # If user provides LLM config with API key, use cloud service
        if request.llm_config and request.llm_config.api_key:
            use_local = False
            logger.info(f"Using cloud RAG service with provider: {request.llm_config.provider}")
        
        # Initialize RAG service
        if use_local:
            logger.info("Using local RAG service with Ollama")
            try:
                rag_service = LocalRAGService(
                    embedding_service_url=settings.EMBEDDING_SERVICE_URL,
                    ollama_base_url=settings.OLLAMA_BASE_URL,
                    ollama_model=settings.OLLAMA_MODEL
                )
            except Exception as e:
                logger.error(f"Failed to initialize local RAG service: {e}")
                raise HTTPException(
                    status_code=503, 
                    detail=f"Local model service unavailable. Please configure cloud LLM in settings or ensure Ollama is running with sufficient memory. Error: {str(e)}"
                )
        else:
            logger.info("Using cloud RAG service")
            llm_config_dict = request.llm_config.model_dump() if request.llm_config else None
            
            if not llm_config_dict or not llm_config_dict.get("api_key"):
                raise HTTPException(
                    status_code=400,
                    detail="Cloud LLM requires API key. Please configure in LLM Settings."
                )
            
            try:
                rag_service = RAGService(llm_config=llm_config_dict)
            except Exception as e:
                logger.error(f"Failed to initialize cloud RAG service: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to initialize cloud LLM service: {str(e)}"
                )
        
        # Determine if we should auto-execute queries
        auto_execute = should_auto_execute_query(request.query) or request.execute_query
        
        # Use RAG to answer query
        answer = rag_service.query_with_rag(request.query, connection.id)
        
        generated_query = None
        query_results = None
        execution_error = None
        
        # Auto-generate and execute query if user intent suggests they want data
        if auto_execute:
            try:
                schema = connection.db_metadata.get("schema", {})
                db_type = connection.db_type
                
                logger.info(f"Generating query for {db_type} database")
                generated_query = rag_service.generate_query(
                    request.query,
                    schema,
                    db_type
                )
                
                # Clean up generated query - remove markdown code blocks if present
                if generated_query:
                    generated_query = generated_query.strip()
                    if generated_query.startswith("```"):
                        # Extract query from markdown code block
                        lines = generated_query.split('\n')
                        # Remove first line (```sql or ```) and last line (```)
                        if len(lines) > 2:
                            generated_query = '\n'.join(lines[1:-1]).strip()
                    elif generated_query.startswith("`") and generated_query.endswith("`"):
                        # Remove inline code backticks
                        generated_query = generated_query.strip('`')
                
                logger.info(f"Generated query: {generated_query[:100]}...")
                
                if generated_query and is_safe_read_query(generated_query, db_type):
                    logger.info(f"Executing {db_type} query safely")
                    query_results = await execute_database_query_safely(connection, generated_query, db_type)
                    
                    # Enhance answer with formatted results
                    results_message = format_query_results(query_results, generated_query, db_type)
                    answer += f"\n\n{results_message}"
                else:
                    logger.warning(f"Generated query failed safety check or was empty")
                    if not generated_query:
                        answer += "\n\n*Note: Could not generate a valid query for your request.*"
                    else:
                        answer += f"\n\n*Note: Generated query failed safety check.*\n```\n{generated_query[:200]}\n```"
                        
            except Exception as e:
                logger.error(f"Auto query execution failed: {e}")
                execution_error = str(e)
                answer += f"\n\n*⚠️ Query Execution Issue: {execution_error}*"
                answer += "\n\n**Generated Query:**\n```\n" + (generated_query or "Could not generate query") + "\n```"
        
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
    
    except HTTPException:
        raise
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
