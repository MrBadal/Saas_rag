from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, DatabaseConnection
from app.services.connectors import get_connector
from app.services.rag_service import RAGService
from app.services.rag_service_local import LocalRAGService
from app.services.schema_store import get_schema_store
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionCreate(BaseModel):
    name: str
    db_type: str
    connection_string: str

class ConnectionResponse(BaseModel):
    id: int
    name: str
    db_type: str
    metadata: Dict[str, Any]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db)
):
    """Create a new database connection and index it for RAG"""
    try:
        # Check if connection with same name already exists
        existing = db.query(DatabaseConnection).filter(
            DatabaseConnection.name == connection.name
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"A connection with name '{connection.name}' already exists")
        
        # Check if connection with same connection string already exists
        existing_string = db.query(DatabaseConnection).filter(
            DatabaseConnection.connection_string == connection.connection_string
        ).first()
        if existing_string:
            raise HTTPException(status_code=400, detail="This database connection already exists")
        
        # Test connection
        connector = get_connector(connection.db_type)
        connector.connect(connection.connection_string)
        
        # Get enhanced schema with metadata
        logger.info(f"Extracting enhanced schema for {connection.db_type} connection")
        schema = connector.get_enhanced_schema()
        
        # Get sample data for RAG
        sample_data = []
        if connection.db_type == "postgresql":
            tables = list(schema.keys())[:5]  # Limit to 5 tables
            for table in tables:
                try:
                    result = connector.execute_query(f"SELECT * FROM {table} LIMIT 10")
                    sample_data.extend(result)
                except Exception as e:
                    logger.warning(f"Could not sample table {table}: {e}")
        
        connector.close()
        
        # Save connection with enhanced schema
        db_connection = DatabaseConnection(
            user_id=1,
            name=connection.name,
            db_type=connection.db_type,
            connection_string=connection.connection_string,
            db_metadata={"schema": schema}
        )
        db.add(db_connection)
        db.commit()
        db.refresh(db_connection)
        
        # Index schema in vector store for intelligent retrieval
        logger.info(f"Indexing schema in vector store for connection {db_connection.id}")
        schema_store = get_schema_store()
        schema_store.index_schema(db_connection.id, schema, connection.db_type)
        
        # Create vector store for RAG with data
        if settings.USE_LOCAL_MODELS:
            logger.info("Using local RAG service for indexing")
            rag_service = LocalRAGService(
                embedding_service_url=settings.EMBEDDING_SERVICE_URL,
                ollama_base_url=settings.OLLAMA_BASE_URL,
                ollama_model=settings.OLLAMA_MODEL
            )
        else:
            logger.info("Using cloud RAG service for indexing")
            rag_service = RAGService()
        
        rag_service.create_vector_store(db_connection.id, schema, sample_data)
        
        logger.info(f"Connection created successfully: {db_connection.name}")
        
        return ConnectionResponse(
            id=db_connection.id,
            name=db_connection.name,
            db_type=db_connection.db_type,
            metadata={"schema": schema}
        )
    
    except Exception as e:
        logger.error(f"Connection creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(db: Session = Depends(get_db)):
    """List all database connections"""
    connections = db.query(DatabaseConnection).all()
    return [
        ConnectionResponse(
            id=conn.id,
            name=conn.name,
            db_type=conn.db_type,
            metadata=conn.db_metadata or {}
        )
        for conn in connections
    ]

@router.delete("/{connection_id}")
async def delete_connection(connection_id: int, db: Session = Depends(get_db)):
    """Delete a database connection"""
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Delete from schema store
    try:
        schema_store = get_schema_store()
        schema_store.delete_schema(connection_id)
        logger.info(f"Deleted schema from vector store for connection {connection_id}")
    except Exception as e:
        logger.warning(f"Failed to delete schema from vector store: {e}")
    
    db.delete(connection)
    db.commit()
    
    logger.info(f"Connection {connection_id} deleted")
    return {"message": "Connection deleted successfully"}

@router.get("/{connection_id}/schema")
async def get_schema(connection_id: int, db: Session = Depends(get_db)):
    """Get database schema for a connection"""
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return connection.db_metadata.get("schema", {})

@router.post("/{connection_id}/refresh-schema")
async def refresh_schema(connection_id: int, db: Session = Depends(get_db)):
    """Refresh database schema for an existing connection"""
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        # Re-extract schema
        connector = get_connector(connection.db_type)
        connector.connect(connection.connection_string)
        
        logger.info(f"Refreshing schema for connection {connection_id}")
        schema = connector.get_enhanced_schema()
        
        # Update connection
        connection.db_metadata = {"schema": schema}
        db.commit()
        
        # Re-index in schema store
        schema_store = get_schema_store()
        schema_store.delete_schema(connection_id)
        schema_store.index_schema(connection_id, schema, connection.db_type)
        
        connector.close()
        
        logger.info(f"Schema refreshed for connection {connection_id}")
        return {"message": "Schema refreshed successfully", "schema": schema}
        
    except Exception as e:
        logger.error(f"Schema refresh failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
