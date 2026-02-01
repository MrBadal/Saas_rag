"""
RAG Service with Self-Hosted Models
- Local embeddings via sentence-transformers
- Local LLM via Ollama
- No external API dependencies
- Optimized for performance
"""
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.services.local_embeddings import LocalEmbeddings
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

class LocalRAGService:
    """RAG Service using completely self-hosted models with performance optimizations"""
    
    def __init__(
        self,
        embedding_service_url: str = "http://localhost:8001",
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2"
    ):
        """
        Initialize RAG service with local models
        
        Args:
            embedding_service_url: URL of local embedding service
            ollama_base_url: URL of Ollama service
            ollama_model: Ollama model name (llama3.2, mistral, phi3, etc.)
        """
        logger.info("Initializing Local RAG Service")
        
        # Initialize local embeddings
        try:
            self.embeddings = LocalEmbeddings(service_url=embedding_service_url)
            logger.info("✓ Local embeddings initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
        
        # Initialize Ollama LLM with performance settings
        try:
            self.llm = Ollama(
                base_url=ollama_base_url,
                model=ollama_model,
                temperature=0,
                num_predict=512,  # Limit response length for faster generation
                top_k=10,  # Reduce sampling space for speed
                top_p=0.9,
                repeat_penalty=1.1
            )
            # Test connection
            test_response = self.llm.invoke("test")
            logger.info(f"✓ Ollama LLM initialized with model: {ollama_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise
        
        # Text splitter for chunking - optimized chunk sizes
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks for faster retrieval
            chunk_overlap=100
        )
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        logger.info("Local RAG Service ready")
    
    def create_vector_store(
        self,
        connection_id: int,
        schema: Dict[str, Any],
        sample_data: List[Dict]
    ):
        """Create vector store from database schema and sample data"""
        logger.info(f"Creating vector store for connection {connection_id}")
        
        # Convert schema and data to text documents
        documents = []
        
        # Add schema information with better formatting
        for table_name, columns in schema.items():
            col_strs = []
            for col in columns:
                col_str = f"{col['name']} ({col['type']})"
                if col.get('primary_key'):
                    col_str += " [PK]"
                if col.get('foreign_key'):
                    col_str += " [FK]"
                col_strs.append(col_str)
            
            schema_text = f"Table: {table_name}\nColumns: {', '.join(col_strs)}\nDescription: Database table containing {table_name} data"
            documents.append(schema_text)
        
        # Add sample data (limit to avoid overwhelming) with better formatting
        for item in sample_data[:30]:  # Reduced sample size for performance
            # Format data more clearly
            formatted_item = json.dumps(item, indent=2, default=str)
            documents.append(f"Sample data:\n{formatted_item}")
        
        logger.info(f"Processing {len(documents)} documents")
        
        # Split documents
        texts = self.text_splitter.create_documents(documents)
        logger.info(f"Split into {len(texts)} chunks")
        
        # Create vector store with pgvector
        collection_name = f"connection_{connection_id}"
        vector_store = PGVector.from_documents(
            documents=texts,
            embedding=self.embeddings,
            collection_name=collection_name,
            connection_string=settings.DATABASE_URL
        )
        
        logger.info(f"✓ Vector store created: {collection_name}")
        return vector_store
    
    def query_with_rag(self, user_query: str, connection_id: int) -> str:
        """Query using RAG - retrieve relevant context and generate answer with performance optimization"""
        start_time = time.time()
        logger.info(f"Processing query for connection {connection_id}")
        
        # Load existing vector store
        collection_name = f"connection_{connection_id}"
        vector_store = PGVector(
            collection_name=collection_name,
            connection_string=settings.DATABASE_URL,
            embedding_function=self.embeddings
        )
        
        # Create optimized prompt for faster processing
        prompt_template = """You are a database assistant. Answer concisely using the context below.

Context: {context}

Question: {question}

Instructions:
- Be direct and concise
- For SQL queries, use proper PostgreSQL syntax
- If suggesting a query, format it clearly
- Limit response to essential information

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain with optimized retrieval
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_kwargs={"k": 2}  # Reduced from 3 to 2 for speed
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False
        )
        
        # Get answer
        result = qa_chain.invoke({"query": user_query})
        
        execution_time = time.time() - start_time
        logger.info(f"✓ Query processed in {execution_time:.2f}s")
        
        return result["result"]
    
    def generate_query(
        self,
        user_intent: str,
        schema: Dict[str, Any],
        db_type: str
    ) -> str:
        """Generate database query from user intent with optimized prompts"""
        logger.info(f"Generating {db_type} query")
        
        # Create concise schema representation
        schema_summary = []
        for table_name, columns in schema.items():
            col_names = [col['name'] for col in columns[:10]]  # Limit columns shown
            schema_summary.append(f"{table_name}({', '.join(col_names)})")
        
        schema_str = "; ".join(schema_summary)
        
        if db_type == "postgresql":
            prompt = f"""Schema: {schema_str}

Generate PostgreSQL query for: {user_intent}

Rules:
- Use SELECT statements only
- Add LIMIT 100 if no limit specified
- Use proper table/column names from schema
- Return only the SQL query

Query:"""
        else:  # mongodb
            prompt = f"""Schema: {schema_str}

Generate MongoDB query for: {user_intent}

Return only the query object as JSON.

Query:"""
        
        response = self.llm.invoke(prompt)
        logger.info("✓ Query generated")
        
        # Clean up response
        query = response.strip()
        if query.startswith("```"):
            # Remove code block markers
            lines = query.split('\n')
            query = '\n'.join(lines[1:-1]) if len(lines) > 2 else query
        
        return query.strip()
