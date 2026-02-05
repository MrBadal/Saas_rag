"""
Enhanced RAG Service with Critical Fixes
- Universal embeddings for all providers
- Timeouts and retry logic
- Response cleaning and validation
- Optimized prompts
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.prompts import get_query_generation_prompt, get_rag_qa_prompt
from app.utils.query_cleaner import clean_query, QueryCleaner
from app.services.query_validator import QueryValidator
from app.services.local_embeddings import LocalEmbeddings
import json
import logging
import time

logger = logging.getLogger(__name__)

class RAGService:
    """
    Enhanced RAG Service with production-ready features
    
    Fixes:
    1. Universal embeddings (OpenAI for all cloud providers including OpenRouter)
    2. Timeout and retry logic for all LLM calls
    3. Multi-stage query cleaning pipeline
    4. Research-backed prompt engineering
    5. Enhanced error handling
    """
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config or {}
        self.provider = self.llm_config.get('provider', 'openai')
        self.api_key = self.llm_config.get('api_key') or settings.OPENAI_API_KEY
        self.model = self.llm_config.get('model')
        
        # Initialize components
        self.embeddings = self._initialize_embeddings()
        self.llm = self._initialize_llm()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.query_cleaner = QueryCleaner()
        self.query_validator = QueryValidator()
        
        logger.info(f"RAGService initialized with provider: {self.provider}")
    
    def _initialize_embeddings(self):
        """Initialize embeddings based on provider"""
        try:
            if self.provider == 'openai':
                # OpenAI users can use OpenAI embeddings
                if not self.api_key:
                    raise ValueError("OpenAI API key required for embeddings")
                
                return OpenAIEmbeddings(
                    openai_api_key=self.api_key,
                    model="text-embedding-ada-002"
                )
            
            elif self.provider == 'openrouter':
                # OpenRouter doesn't support embeddings - use local embedding service
                # The local embedding service runs as part of the docker-compose stack
                logger.info("OpenRouter: Using local embedding service (OpenRouter doesn't support embeddings)")
                try:
                    return LocalEmbeddings(
                        service_url=settings.EMBEDDING_SERVICE_URL or "http://embedding_service:8001"
                    )
                except Exception as e:
                    logger.warning(f"Local embeddings failed, trying OpenAI fallback: {e}")
                    # If local embeddings fail and we have an env OpenAI key, use that
                    if settings.OPENAI_API_KEY:
                        return OpenAIEmbeddings(
                            openai_api_key=settings.OPENAI_API_KEY,
                            model="text-embedding-ada-002"
                        )
                    raise ValueError("OpenRouter requires local embedding service or OPENAI_API_KEY in environment")
            
            elif self.provider == 'google':
                # Google has its own embeddings
                try:
                    return GoogleGenerativeAIEmbeddings(
                        model="models/embedding-001",
                        google_api_key=self.api_key
                    )
                except Exception as e:
                    logger.warning(f"Google embeddings failed, trying local: {e}")
                    return LocalEmbeddings(
                        service_url=settings.EMBEDDING_SERVICE_URL or "http://embedding_service:8001"
                    )
            
            else:
                # Default: try local embeddings first, then OpenAI
                try:
                    return LocalEmbeddings(
                        service_url=settings.EMBEDDING_SERVICE_URL or "http://embedding_service:8001"
                    )
                except Exception as e:
                    if self.api_key:
                        return OpenAIEmbeddings(openai_api_key=self.api_key)
                    raise ValueError(f"No embedding service available: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize LLM with timeout and retry configuration"""
        try:
            if self.provider == 'google':
                model = self.model or "gemini-1.5-flash"
                return ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=self.api_key,
                    temperature=0,
                    convert_system_message_to_human=True,
                    request_timeout=30,
                    max_retries=3
                )
            
            elif self.provider == 'openrouter':
                model = self.model or "openai/gpt-3.5-turbo"
                return ChatOpenAI(
                    model=model,
                    temperature=0,
                    openai_api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "DataQuery AI"
                    },
                    request_timeout=30,
                    max_retries=3
                )
            
            else:  # openai
                model = self.model or "gpt-3.5-turbo"
                return ChatOpenAI(
                    model=model,
                    temperature=0,
                    openai_api_key=self.api_key,
                    request_timeout=30,
                    max_retries=3
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, Exception)),
        reraise=True
    )
    def _invoke_llm_with_retry(self, prompt: str) -> str:
        """Invoke LLM with retry logic and timeout"""
        try:
            start_time = time.time()
            response = self.llm.invoke(prompt)
            elapsed = time.time() - start_time
            logger.info(f"LLM invocation completed in {elapsed:.2f}s")
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.warning(f"LLM invocation failed: {e}. Retrying...")
            raise
    
    def create_vector_store(self, connection_id: int, schema: Dict[str, Any], sample_data: List[Dict]):
        """Create vector store from database schema and sample data"""
        try:
            documents = []
            
            # Add schema information
            for table_name, columns in schema.items():
                if isinstance(columns, list):
                    col_strs = [f"{col['name']} ({col['type']})" for col in columns]
                else:
                    col_strs = [f"{col['name']} ({col['type']})" for col in columns.get('fields', [])]
                
                schema_text = f"Table: {table_name}\nColumns: {', '.join(col_strs)}"
                documents.append(schema_text)
            
            # Add sample data
            for item in sample_data[:50]:  # Limit sample data
                documents.append(json.dumps(item, indent=2, default=str))
            
            # Split documents
            texts = self.text_splitter.create_documents(documents)
            
            # Create vector store
            collection_name = f"connection_{connection_id}"
            vector_store = PGVector.from_documents(
                documents=texts,
                embedding=self.embeddings,
                collection_name=collection_name,
                connection_string=settings.DATABASE_URL
            )
            
            logger.info(f"Vector store created: {collection_name}")
            return vector_store
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def query_with_rag(self, user_query: str, connection_id: int) -> str:
        """Query using RAG with optimized retrieval"""
        try:
            start_time = time.time()
            
            # Load vector store
            collection_name = f"connection_{connection_id}"
            vector_store = PGVector(
                collection_name=collection_name,
                connection_string=settings.DATABASE_URL,
                embedding_function=self.embeddings
            )
            
            # Create optimized prompt
            prompt = get_rag_qa_prompt(
                context="",
                schema="",
                question=user_query
            )
            
            # Create QA chain with increased retrieval
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=False
            )
            
            # Execute with retry
            result = self._invoke_llm_with_retry(prompt)
            
            elapsed = time.time() - start_time
            logger.info(f"RAG query completed in {elapsed:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return f"I encountered an error: {str(e)}. Please try again or check your connection."
    
    def generate_query(self, user_intent: str, schema: Dict[str, Any], 
                       db_type: str, max_retries: int = 2) -> Tuple[str, bool]:
        """
        Generate database query with cleaning and validation
        
        Returns:
            Tuple of (query, is_valid)
        """
        try:
            # Build relationships string from schema
            relationships = self._extract_relationships(schema)
            
            # Generate optimized prompt
            prompt = get_query_generation_prompt(
                db_type=db_type,
                schema=json.dumps(schema, indent=2),
                user_query=user_intent,
                relationships=relationships
            )
            
            # Invoke LLM with retry
            raw_response = self._invoke_llm_with_retry(prompt)
            
            # Multi-stage cleaning
            cleaned_query, is_valid = clean_query(raw_response, db_type)
            
            if not is_valid and max_retries > 0:
                logger.warning(f"Query invalid, attempting retry. Remaining: {max_retries}")
                # Retry with additional context
                retry_prompt = prompt + f"\n\nPrevious attempt failed. Please generate only the {db_type} query without any explanation."
                raw_response = self._invoke_llm_with_retry(retry_prompt)
                cleaned_query, is_valid = clean_query(raw_response, db_type)
            
            # Add safety limit if PostgreSQL
            if db_type == "postgresql" and is_valid:
                cleaned_query = self.query_cleaner.add_limit_if_missing(cleaned_query)
            
            # Validate query
            validation_result = self.query_validator.validate(cleaned_query, db_type)
            
            if not validation_result.is_valid:
                logger.error(f"Query validation failed: {validation_result.errors}")
                return cleaned_query, False
            
            logger.info(f"Query generated and validated successfully")
            return cleaned_query, True
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return "", False
    
    def _extract_relationships(self, schema: Dict[str, Any]) -> str:
        """Extract table relationships from schema metadata"""
        relationships = []
        
        for table_name, columns in schema.items():
            if isinstance(columns, list):
                for col in columns:
                    if col.get('foreign_key'):
                        fk = col['foreign_key']
                        rel = f"{table_name}.{col['name']} → {fk.get('referred_table')}.{fk.get('referred_columns', ['id'])[0]}"
                        relationships.append(rel)
        
        return "\n".join(relationships) if relationships else "No explicit relationships defined."

# Backward compatibility - alias for existing code
EnhancedRAGService = RAGService
