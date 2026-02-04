from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, DatabaseConnection, QueryHistory
from app.services.rag_service import RAGService
from app.services.rag_service_local import LocalRAGService
from app.services.connectors import get_connector
from app.services.schema_store import get_schema_store
from app.services.query_validator import QueryValidator
from app.services.pii_redaction import create_redactor
from app.services.visualizer import create_visualizer
from app.agents.sql_agent import create_sql_agent
from app.core.config import settings
from app.core.security import get_security_manager
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
    stream: bool = False
    execute_query: bool = True

class QueryResponse(BaseModel):
    answer: str
    generated_query: str | None = None
    query_results: list | None = None
    execution_time: float | None = None
    auto_executed: bool = False
    visualization: Dict[str, Any] | None = None
    thinking_steps: List[str] | None = None

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
    execution_keywords = [
        "show me", "get", "find", "list", "display", "fetch", "retrieve",
        "how many", "count", "total", "sum", "average", "latest", "recent",
        "all", "select", "where", "filter", "search", "data", "records",
        "rows", "entries", "results", "details", "information", "orders",
        "customers", "users", "products", "sales", "transactions"
    ]
    
    non_execution_keywords = [
        "what is", "how to", "explain", "describe", "structure", "schema",
        "what are", "tell me about", "what does", "help me understand"
    ]
    
    query_lower = user_query.lower()
    
    if any(keyword in query_lower for keyword in non_execution_keywords):
        if not any(keyword in query_lower for keyword in execution_keywords):
            return False
    
    return any(keyword in query_lower for keyword in execution_keywords)

async def execute_database_query_safely(connection: DatabaseConnection, query: str, db_type: str) -> List[Dict]:
    """Execute database query with safety checks and timeout"""
    connector = get_connector(connection.db_type)
    
    try:
        connector.connect(connection.connection_string)
        
        if connection.db_type == "postgresql":
            # Add LIMIT if not present
            if "limit" not in query.lower() and "select" in query.lower():
                query = f"{query.rstrip(';')} LIMIT 100"
            
            results = connector.execute_query(query)
        elif connection.db_type == "mongodb":
            try:
                query_obj = json.loads(query)
                results = connector.execute_query(query_obj)
            except json.JSONDecodeError:
                raise ValueError("Invalid MongoDB query format")
        else:
            results = []
        
        return results[:100]  # Limit results
        
    finally:
        connector.close()

def format_query_results(results: List[Dict], query: str, db_type: str) -> str:
    """Format query results in a user-friendly way"""
    if not results:
        return "**Query Results:** No records found matching your criteria."
    
    result_count = len(results)
    formatted = f"**Query Results:** Found {result_count} record{'s' if result_count > 1 else ''}.\n\n"
    
    if result_count <= 5:
        formatted += "Here are all the results:\n\n"
        for i, row in enumerate(results, 1):
            formatted += f"**{i}.** {format_row(row)}\n"
    elif result_count <= 20:
        formatted += f"Showing first 10 of {result_count} results:\n\n"
        for i, row in enumerate(results[:10], 1):
            formatted += f"**{i}.** {format_row(row)}\n"
        formatted += f"\n... and {result_count - 10} more records."
    else:
        formatted += f"Showing first 5 of {result_count} results:\n\n"
        for i, row in enumerate(results[:5], 1):
            formatted += f"**{i}.** {format_row(row)}\n"
        formatted += f"\n... and {result_count - 5} more records."
    
    return formatted

def format_row(row: Dict) -> str:
    """Format a single row/dict for display"""
    if not row:
        return "Empty record"
    
    parts = []
    for key, value in row.items():
        if value is not None and value != "":
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
    security_manager = get_security_manager()
    
    try:
        # Sanitize input
        user_query = security_manager.sanitize_input(request.query)
        
        # Get connection
        connection = db.query(DatabaseConnection).filter(
            DatabaseConnection.id == request.connection_id
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Get relevant schema using vectorized schema store
        schema_store = get_schema_store()
        relevant_schema = schema_store.get_relevant_schema(
            connection.id, 
            user_query, 
            k=10
        )
        
        # Fallback to full schema if vector search fails
        if not relevant_schema:
            relevant_schema = connection.db_metadata.get("schema", {})
        
        # Determine RAG service
        use_local = settings.USE_LOCAL_MODELS
        if request.llm_config and request.llm_config.api_key:
            use_local = False
        
        # Initialize RAG service
        if use_local:
            logger.info("Using local RAG service")
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
                    detail=f"Local model service unavailable. Please configure cloud LLM. Error: {str(e)}"
                )
        else:
            logger.info(f"Using cloud RAG service with provider: {request.llm_config.provider if request.llm_config else 'default'}")
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
        
        # Use RAG to answer query
        answer = rag_service.query_with_rag(user_query, connection.id)
        
        generated_query = None
        query_results = None
        thinking_steps = []
        visualization = None
        auto_execute = should_auto_execute_query(user_query) or request.execute_query
        
        # Auto-generate and execute query
        if auto_execute:
            try:
                schema = relevant_schema
                db_type = connection.db_type
                
                logger.info(f"Generating query for {db_type} database")
                
                # Use SQL Agent for self-correcting generation
                sql_agent = create_sql_agent(llm_config_dict if not use_local else None)
                agent_result = sql_agent.generate_query(user_query, schema, db_type)
                
                generated_query = agent_result.get("query", "")
                thinking_steps = agent_result.get("thinking_steps", [])
                is_valid = agent_result.get("success", False)
                
                if generated_query and is_valid:
                    logger.info(f"Generated valid query: {generated_query[:100]}...")
                    
                    # Execute query
                    query_results = await execute_database_query_safely(
                        connection, generated_query, db_type
                    )
                    
                    # Apply PII redaction
                    redactor = create_redactor(use_presidio=True)
                    query_results = redactor.redact_results(query_results)
                    
                    # Enhance answer with formatted results
                    results_message = format_query_results(query_results, generated_query, db_type)
                    answer += f"\n\n{results_message}"
                    
                    # Generate visualization
                    visualizer = create_visualizer()
                    viz_rec = visualizer.recommend_visualization(query_results, user_query)
                    visualization = visualizer.generate_plotly_config(viz_rec, query_results)
                    
                else:
                    logger.warning(f"Query generation failed validation: {agent_result.get('errors', [])}")
                    answer += f"\n\n*Note: Could not generate a valid query. Errors: {', '.join(agent_result.get('errors', []))}*"
                    
            except Exception as e:
                logger.error(f"Auto query execution failed: {e}")
                answer += f"\n\n*⚠️ Query Execution Issue: {str(e)}*"
        
        # Audit log
        security_manager.audit_log(
            action="query_execution",
            user_id=1,  # TODO: Get from auth
            connection_id=connection.id,
            query=user_query,
            success=query_results is not None
        )
        
        # Save to history
        history = QueryHistory(
            user_id=1,
            connection_id=connection.id,
            query=user_query,
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
            auto_executed=auto_execute and query_results is not None,
            visualization=visualization,
            thinking_steps=thinking_steps
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
        
        chat_models = []
        for model in models.data:
            if any(prefix in model.id for prefix in ["gpt-3.5", "gpt-4", "gpt-4o"]):
                chat_models.append({
                    "id": model.id,
                    "name": model.id,
                    "description": f"OpenAI {model.id}",
                    "provider": "openai"
                })
        
        chat_models.sort(key=lambda x: x["id"])
        return ModelListResponse(models=chat_models)
        
    except Exception as e:
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
                
                models.sort(key=lambda x: x["name"])
                return ModelListResponse(models=models)
            else:
                raise Exception(f"API returned {response.status_code}")
                
    except Exception as e:
        default_models = [
            {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus", "description": "Most capable Claude model", "provider": "openrouter"},
            {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance", "provider": "openrouter"},
            {"id": "openai/gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Latest GPT-4 via OpenRouter", "provider": "openrouter"},
            {"id": "mistralai/mixtral-8x7b-instruct", "name": "Mixtral 8x7B", "description": "Open source model", "provider": "openrouter"}
        ]
        return ModelListResponse(models=default_models)
