from typing import Dict, Any, List
from sqlalchemy import create_engine, inspect
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Base class for database connectors"""
    
    def connect(self, connection_string: str):
        raise NotImplementedError
    
    def get_schema(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def execute_query(self, query: str) -> List[Dict]:
        raise NotImplementedError

class PostgreSQLConnector(DatabaseConnector):
    def __init__(self):
        self.engine = None
        self.connection = None
    
    def connect(self, connection_string: str):
        try:
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            logger.info("PostgreSQL connection established")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        inspector = inspect(self.engine)
        schema = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"])
                })
            schema[table_name] = columns
        
        return schema
    
    def execute_query(self, query: str) -> List[Dict]:
        result = self.connection.execute(query)
        return [dict(row) for row in result]
    
    def close(self):
        if self.connection:
            self.connection.close()

class MongoDBConnector(DatabaseConnector):
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self, connection_string: str):
        try:
            self.client = MongoClient(connection_string)
            # Extract database name from connection string
            # Handle various MongoDB connection string formats
            # Format: mongodb+srv://user:pass@host/dbname?options or mongodb://user:pass@host:port/dbname?options
            db_name = connection_string.split("/")[-1].split("?")[0]
            
            # If no database name in URL (empty string), use 'admin' as default or list available databases
            if not db_name:
                # Try to get the first available database (excluding system databases)
                server_info = self.client.server_info()
                logger.info(f"MongoDB server info: {server_info}")
                # List database names and pick first non-system one
                db_names = self.client.list_database_names()
                non_system_dbs = [db for db in db_names if db not in ['admin', 'local', 'config']]
                if non_system_dbs:
                    db_name = non_system_dbs[0]
                else:
                    db_name = 'admin'  # fallback
                logger.info(f"No database specified, using: {db_name}")
            
            self.db = self.client[db_name]
            logger.info(f"MongoDB connection established to database: {db_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        schema = {}
        
        for collection_name in self.db.list_collection_names():
            # Sample first document to infer schema
            sample = self.db[collection_name].find_one()
            if sample:
                fields = list(sample.keys())
                schema[collection_name] = [{"name": field, "type": "mixed"} for field in fields]
        
        return schema
    
    def execute_query(self, query: str) -> List[Dict]:
        """Execute MongoDB query from JSON string
        
        Expected query format (JSON):
        {
          "collection": "orders",
          "filter": {"status": "completed"},
          "limit": 100
        }
        """
        try:
            import json
            query_obj = json.loads(query) if isinstance(query, str) else query
            
            # Extract collection and filter
            collection_name = query_obj.get('collection')
            filter_dict = query_obj.get('filter', {})
            limit = query_obj.get('limit', 100)
            
            if not collection_name:
                # Try to infer collection from available collections
                collections = self.db.list_collection_names()
                if collections:
                    collection_name = collections[0]
                    logger.info(f"No collection specified, using: {collection_name}")
                else:
                    raise ValueError("No collection specified and no collections found in database")
            
            # Execute query
            cursor = self.db[collection_name].find(filter_dict).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON query: {e}")
            raise ValueError(f"Invalid JSON query format: {e}")
        except Exception as e:
            logger.error(f"MongoDB query execution failed: {e}")
            raise
    
    def close(self):
        if self.client:
            self.client.close()

def get_connector(db_type: str) -> DatabaseConnector:
    """Factory function to get appropriate connector"""
    connectors = {
        "postgresql": PostgreSQLConnector,
        "mongodb": MongoDBConnector
    }
    
    connector_class = connectors.get(db_type.lower())
    if not connector_class:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    return connector_class()
