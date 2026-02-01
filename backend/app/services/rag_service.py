from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.core.config import settings
import json

class RAGService:
    def __init__(self, llm_config: Dict[str, Any] = None):
        # Default configuration from env
        provider = "openai"
        api_key = settings.OPENAI_API_KEY
        model = "gpt-3.5-turbo"
        
        # Override with user config if provided
        if llm_config:
            if llm_config.get("provider"):
                provider = llm_config.get("provider")
            
            # CRITICAL: Prefer user provided key, even if it's for OpenAI
            if llm_config.get("api_key") and llm_config.get("api_key").strip():
                api_key = llm_config.get("api_key")
            elif provider == "openai" and not api_key: 
                 # If no user key and no env key for OpenAI, we have a problem
                 pass 
            
            if llm_config.get("model"):
                model = llm_config.get("model")
            
            if llm_config.get("model"):
                model = llm_config.get("model")
            else:
                # Set default model based on provider if not explicitly provided
                if provider == "google":
                    model = "gemini-1.5-flash"
                elif provider == "openrouter":
                    model = "openai/gpt-3.5-turbo" # OpenRouter convention
                elif provider == "openai":
                    model = "gpt-3.5-turbo"
        
        # Initialize Embeddings based on provider
        if provider == "google":
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
        elif provider == "openrouter":
            # OpenRouter support using OpenAI compatible embeddings
            # Assuming user key works for embeddings on OpenRouter or is compatible
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                model="text-embedding-ada-002"
            )
        else:
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        
        if provider == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0,
                convert_system_message_to_human=True
            )
        elif provider == "openrouter":
            self.llm = ChatOpenAI(
                model=model,
                temperature=0,
                openai_api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "DataQuery AI"
                }
            )
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=0,
                openai_api_key=api_key
            )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def create_vector_store(self, connection_id: int, schema: Dict[str, Any], sample_data: List[Dict]):
        """Create vector store from database schema and sample data"""
        
        # Convert schema and data to text documents
        documents = []
        
        # Add schema information
        for table_name, columns in schema.items():
            col_strs = [f"{col['name']} ({col['type']})" for col in columns]
            schema_text = f"Table: {table_name}\nColumns: {', '.join(col_strs)}"
            documents.append(schema_text)
        
        # Add sample data
        for item in sample_data:
            documents.append(json.dumps(item, indent=2))
        
        # Split documents
        texts = self.text_splitter.create_documents(documents)
        
        # Create vector store with pgvector
        collection_name = f"connection_{connection_id}"
        vector_store = PGVector.from_documents(
            documents=texts,
            embedding=self.embeddings,
            collection_name=collection_name,
            connection_string=settings.DATABASE_URL
        )
        
        return vector_store
    
    def query_with_rag(self, user_query: str, connection_id: int) -> str:
        """Query using RAG - retrieve relevant context and generate answer"""
        
        # Load existing vector store
        collection_name = f"connection_{connection_id}"
        vector_store = PGVector(
            collection_name=collection_name,
            connection_string=settings.DATABASE_URL,
            embedding_function=self.embeddings
        )
        
        # Create custom prompt
        prompt_template = """You are an AI assistant helping users query their database.
        Use the following context about the database schema and data to answer the question.
        If you need to suggest a query, provide it in the appropriate format (SQL for PostgreSQL, MongoDB query for MongoDB).
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        # Get answer
        result = qa_chain.invoke({"query": user_query})
        return result["result"]
    
    def generate_query(self, user_intent: str, schema: Dict[str, Any], db_type: str) -> str:
        """Generate database query from user intent"""
        
        schema_str = json.dumps(schema, indent=2)
        
        if db_type == "postgresql":
            prompt = f"""Given this PostgreSQL database schema:
{schema_str}

Generate a SQL query for: {user_intent}

Return only the SQL query, no explanation."""
        else:  # mongodb
            prompt = f"""Given this MongoDB database schema:
{schema_str}

Generate a MongoDB query (as JSON) for: {user_intent}

Return only the query object, no explanation."""
        
        response = self.llm.invoke(prompt)
        return response.content
