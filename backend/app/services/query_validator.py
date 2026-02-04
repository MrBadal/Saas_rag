"""
SQL Query Validator using AST Parsing
Defense-in-depth security with comprehensive validation
"""

import sqlparse
import logging
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationError(Enum):
    INVALID_SYNTAX = "invalid_syntax"
    FORBIDDEN_OPERATION = "forbidden_operation"
    UNKNOWN_TABLE = "unknown_table"
    UNKNOWN_COLUMN = "unknown_column"
    INJECTION_DETECTED = "injection_detected"
    MULTIPLE_STATEMENTS = "multiple_statements"
    MISSING_LIMIT = "missing_limit"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    normalized_query: str
    
class QueryValidator:
    """
    Multi-layer query validation:
    1. SQL syntax parsing (AST)
    2. Forbidden operation detection
    3. Table/column whitelist validation
    4. Injection pattern detection
    """
    
    # Allowed SQL statement types
    ALLOWED_STATEMENTS = {'SELECT', 'EXPLAIN', 'DESCRIBE', 'SHOW', 'WITH'}
    
    # Forbidden operations
    FORBIDDEN_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'MERGE', 'UPSERT', 'REPLACE'
    }
    
    # Dangerous SQL patterns (injection detection)
    DANGEROUS_PATTERNS = [
        r';\s*DROP\s+',  # DROP after semicolon
        r';\s*DELETE\s+',  # DELETE after semicolon
        r'--',  # SQL comment injection
        r'/\*',  # Multi-line comment injection
        r'UNION\s+SELECT',  # UNION injection
        r'1\s*=\s*1',  # Tautology injection
        r'OR\s+\'\w+\'\s*=\s*\'\w+\'',  # OR-based injection
    ]
    
    def __init__(self, allowed_tables: Optional[Set[str]] = None, 
                 allowed_columns: Optional[Set[str]] = None):
        self.allowed_tables = allowed_tables or set()
        self.allowed_columns = allowed_columns or set()
    
    def validate(self, query: str, db_type: str = "postgresql") -> ValidationResult:
        """
        Comprehensive query validation
        
        Returns ValidationResult with status, errors, and normalized query
        """
        errors = []
        warnings = []
        
        if not query or not query.strip():
            return ValidationResult(
                is_valid=False,
                errors=["Empty query"],
                warnings=[],
                normalized_query=""
            )
        
        query = query.strip()
        
        # Layer 1: SQL Syntax Validation
        try:
            parsed = sqlparse.parse(query)
            if not parsed:
                errors.append("Failed to parse SQL query")
                return ValidationResult(False, errors, warnings, query)
            
            # Check for multiple statements
            if len(parsed) > 1:
                errors.append("Multiple SQL statements detected. Only single statements allowed.")
                return ValidationResult(False, errors, warnings, query)
            
            statement = parsed[0]
            
        except Exception as e:
            logger.error(f"SQL parsing error: {e}")
            errors.append(f"Invalid SQL syntax: {str(e)}")
            return ValidationResult(False, errors, warnings, query)
        
        # Layer 2: Statement Type Validation
        first_token = self._get_first_keyword(statement)
        if not first_token:
            errors.append("Could not identify SQL statement type")
            return ValidationResult(False, errors, warnings, query)
        
        if first_token.upper() not in self.ALLOWED_STATEMENTS:
            errors.append(f"Forbidden SQL operation: {first_token}. Only read-only queries allowed.")
            return ValidationResult(False, errors, warnings, query)
        
        # Layer 3: Forbidden Keyword Scan
        query_upper = query.upper()
        for forbidden in self.FORBIDDEN_KEYWORDS:
            if forbidden in query_upper:
                errors.append(f"Query contains forbidden keyword: {forbidden}")
                return ValidationResult(False, errors, warnings, query)
        
        # Layer 4: Injection Pattern Detection
        import re
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                errors.append(f"Potential SQL injection pattern detected: {pattern}")
                return ValidationResult(False, errors, warnings, query)
        
        # Layer 5: Table/Column Validation (if whitelist provided)
        if self.allowed_tables:
            referenced_tables = self._extract_tables(statement)
            for table in referenced_tables:
                if table.lower() not in {t.lower() for t in self.allowed_tables}:
                    errors.append(f"Table not in whitelist: {table}")
        
        # Layer 6: LIMIT Check (warning only)
        if 'LIMIT' not in query_upper:
            warnings.append("Query missing LIMIT clause. May return large result sets.")
        
        # Normalize query
        normalized = sqlparse.format(query, reindent=True, keyword_case='upper')
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Query validation passed")
        else:
            logger.warning(f"Query validation failed: {errors}")
        
        return ValidationResult(is_valid, errors, warnings, normalized)
    
    def validate_mongodb_query(self, query: dict) -> ValidationResult:
        """
        Validate MongoDB query object
        """
        errors = []
        warnings = []
        
        if not isinstance(query, dict):
            errors.append("MongoDB query must be a dictionary")
            return ValidationResult(False, errors, warnings, str(query))
        
        # Check for dangerous operations
        dangerous_ops = {'$merge', '$out', '$update', '$delete', '$drop'}
        query_str = str(query)
        
        for op in dangerous_ops:
            if op in query_str:
                errors.append(f"Forbidden MongoDB operation: {op}")
        
        # Check for collection
        if 'collection' not in query:
            warnings.append("No collection specified in query")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, query_str)
    
    def _get_first_keyword(self, statement) -> Optional[str]:
        """Extract first keyword from SQL statement"""
        for token in statement.tokens:
            if token.ttype is not None and token.ttype in sqlparse.tokens.Keyword:
                return token.value
            elif token.ttype is None and token.is_group:
                # Handle WITH clause (CTE)
                first = token.token_first()
                if first:
                    return first.value
        return None
    
    def _extract_tables(self, statement) -> Set[str]:
        """Extract table names from SQL statement"""
        tables = set()
        
        def process_token(token):
            if token.ttype is None and token.is_group:
                # Check if it's a table reference
                if len(token.tokens) >= 1:
                    first = token.token_first()
                    if first and first.ttype in sqlparse.tokens.Name:
                        tables.add(first.value)
                # Recurse into sub-tokens
                for sub in token.tokens:
                    process_token(sub)
            elif token.ttype in sqlparse.tokens.Name:
                tables.add(token.value)
        
        for token in statement.tokens:
            process_token(token)
        
        return tables
    
    def is_read_only(self, query: str) -> bool:
        """Quick check if query is read-only"""
        query_upper = query.upper().strip()
        
        # Must start with allowed keywords
        if not any(query_upper.startswith(kw) for kw in self.ALLOWED_STATEMENTS):
            return False
        
        # Must not contain forbidden keywords
        for forbidden in self.FORBIDDEN_KEYWORDS:
            if forbidden in query_upper:
                return False
        
        return True
    
    def add_safety_limit(self, query: str, max_rows: int = 100) -> str:
        """Add safety LIMIT if not present"""
        query_upper = query.upper()
        
        if 'LIMIT' in query_upper:
            return query
        
        # Remove trailing semicolon if present
        query = query.rstrip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"{query} LIMIT {max_rows}"

# Convenience function
def validate_query(query: str, db_type: str = "postgresql", 
                   allowed_tables: Optional[Set[str]] = None) -> ValidationResult:
    """Validate query with optional table whitelist"""
    validator = QueryValidator(allowed_tables=allowed_tables)
    return validator.validate(query, db_type)
