from typing import Dict, Any, List
from sqlalchemy import create_engine, inspect, text
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Base class for database connectors"""
    
    def connect(self, connection_string: str):
        raise NotImplementedError
    
    def get_schema(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def get_enhanced_schema(self) -> Dict[str, Any]:
        """Get schema with metadata (PK, FK, indexes)"""
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
        """Basic schema extraction"""
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
    
    def get_enhanced_schema(self) -> Dict[str, Any]:
        """
        Enhanced schema with PK, FK, indexes, and relationships
        """
        inspector = inspect(self.engine)
        schema = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            
            # Get primary key
            pk_columns = set()
            try:
                pk_info = inspector.get_pk_constraint(table_name)
                pk_columns = set(pk_info.get('constrained_columns', []))
            except Exception as e:
                logger.warning(f"Could not get PK for {table_name}: {e}")
            
            # Get foreign keys
            fk_info = {}
            try:
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    for col in fk.get('constrained_columns', []):
                        fk_info[col] = {
                            'referred_table': fk.get('referred_table'),
                            'referred_columns': fk.get('referred_columns', [])
                        }
            except Exception as e:
                logger.warning(f"Could not get FK for {table_name}: {e}")
            
            # Get indexes
            indexes = {}
            try:
                idx_info = inspector.get_indexes(table_name)
                for idx in idx_info:
                    for col in idx.get('column_names', []):
                        indexes[col] = idx.get('unique', False)
            except Exception as e:
                logger.warning(f"Could not get indexes for {table_name}: {e}")
            
            # Build column info
            for column in inspector.get_columns(table_name):
                col_name = column["name"]
                col_info = {
                    "name": col_name,
                    "type": str(column["type"]),
                    "nullable": column.get("nullable", True),
                    "default": str(column.get("default")) if column.get("default") else None,
                    "primary_key": col_name in pk_columns,
                    "foreign_key": fk_info.get(col_name),
                    "indexed": col_name in indexes,
                    "unique": indexes.get(col_name, False)
                }
                columns.append(col_info)
            
            schema[table_name] = columns
        
        return schema
    
    def execute_query(self, query: str) -> List[Dict]:
        result = self.connection.execute(text(query))
        return [dict(row._mapping) for row in result]
    
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
            db_name = connection_string.split("/")[-1].split("?")[0]
            
            if not db_name:
                # Try to get the first available database
                db_names = self.client.list_database_names()
                non_system_dbs = [db for db in db_names if db not in ['admin', 'local', 'config']]
                db_name = non_system_dbs[0] if non_system_dbs else 'admin'
                logger.info(f"No database specified, using: {db_name}")
            
            self.db = self.client[db_name]
            logger.info(f"MongoDB connection established to database: {db_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Basic schema extraction from sample documents"""
        schema = {}
        
        for collection_name in self.db.list_collection_names():
            # Sample first document to infer schema
            sample = self.db[collection_name].find_one()
            if sample:
                fields = []
                for key, value in sample.items():
                    field_type = type(value).__name__
                    fields.append({
                        "name": key,
                        "type": field_type
                    })
                schema[collection_name] = fields
        
        return schema
    
    def get_enhanced_schema(self) -> Dict[str, Any]:
        """
        Enhanced schema with statistics and index information
        """
        schema = {}
        
        for collection_name in self.db.list_collection_names():
            collection = self.db[collection_name]
            
            # Sample documents for field inference
            samples = list(collection.find().limit(100))
            
            if samples:
                # Infer fields from multiple samples
                field_types = {}
                for sample in samples:
                    for key, value in sample.items():
                        if key not in field_types:
                            field_types[key] = set()
                        field_types[key].add(type(value).__name__)
                
                fields = []
                for key, types in field_types.items():
                    # Get most common type
                    type_str = list(types)[0] if len(types) == 1 else f"Union[{', '.join(types)}]"
                    
                    # Check if field is indexed
                    is_indexed = False
                    try:
                        indexes = collection.list_indexes()
                        for idx in indexes:
                            if key in idx.get('key', {}):
                                is_indexed = True
                                break
                    except:
                        pass
                    
                    fields.append({
                        "name": key,
                        "type": type_str,
                        "indexed": is_indexed,
                        "sample_count": len([s for s in samples if key in s])
                    })
                
                # Add collection statistics
                stats = {}
                try:
                    stats = self.db.command("collStats", collection_name)
                except:
                    pass
                
                schema[collection_name] = {
                    "fields": fields,
                    "document_count": stats.get('count', collection.count_documents({})),
                    "size_bytes": stats.get('size', 0),
                    "avg_document_size": stats.get('avgObjSize', 0)
                }
            else:
                schema[collection_name] = {"fields": [], "document_count": 0}
        
        return schema
    
    def execute_query(self, query: str) -> List[Dict]:
        """Execute MongoDB query from JSON string"""
        try:
            import json
            query_obj = json.loads(query) if isinstance(query, str) else query
            
            # Extract collection and filter
            collection_name = query_obj.get('collection')
            filter_dict = query_obj.get('filter', {})
            limit = query_obj.get('limit', 100)
            
            if not collection_name:
                collections = self.db.list_collection_names()
                if collections:
                    collection_name = collections[0]
                else:
                    raise ValueError("No collection specified and no collections found")
            
            # Execute query
            cursor = self.db[collection_name].find(filter_dict).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string
            def convert_objectids(obj):
                from bson import ObjectId
                from datetime import datetime
                
                if isinstance(obj, ObjectId):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_objectids(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_objectids(item) for item in obj]
                else:
                    return obj
            
            return [convert_objectids(doc) for doc in results]
            
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
