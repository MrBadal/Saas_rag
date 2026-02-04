"""
Query Cleaning and Validation Utilities
Multi-stage cleaning pipeline for LLM-generated queries
"""

import re
import json
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class QueryCleaner:
    """
    Multi-stage query cleaning pipeline:
    1. Extract from markdown blocks
    2. Remove comments
    3. Strip explanations
    4. Validate format
    """
    
    @staticmethod
    def clean_sql_query(raw_query: str) -> Tuple[str, bool]:
        """
        Clean SQL query from LLM output
        
        Returns:
            Tuple of (cleaned_query, is_valid)
        """
        if not raw_query:
            return "", False
        
        query = raw_query.strip()
        
        # Stage 1: Extract from markdown code blocks
        query = QueryCleaner._extract_from_markdown(query)
        
        # Stage 2: Remove inline comments
        query = QueryCleaner._remove_sql_comments(query)
        
        # Stage 3: Strip explanations
        query = QueryCleaner._strip_explanations(query)
        
        # Stage 4: Basic validation
        is_valid = QueryCleaner._validate_sql_format(query)
        
        return query.strip(), is_valid
    
    @staticmethod
    def clean_mongodb_query(raw_query: str) -> Tuple[str, bool]:
        """
        Clean MongoDB query from LLM output
        
        Returns:
            Tuple of (cleaned_query, is_valid)
        """
        if not raw_query:
            return "", False
        
        query = raw_query.strip()
        
        # Stage 1: Extract from markdown
        query = QueryCleaner._extract_from_markdown(query)
        
        # Stage 2: Try to parse as JSON
        try:
            query_obj = json.loads(query)
            # Re-serialize to ensure valid JSON
            return json.dumps(query_obj), True
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in MongoDB query: {query[:100]}")
            return query, False
    
    @staticmethod
    def _extract_from_markdown(text: str) -> str:
        """Extract content from markdown code blocks"""
        # Handle ```sql ... ``` or ```json ... ```
        patterns = [
            r'```sql\s*\n(.*?)\n```',  # SQL code block
            r'```json\s*\n(.*?)\n```',  # JSON code block
            r'```\s*\n(.*?)\n```',  # Generic code block
            r'`(.*?)`',  # Inline code
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return text
    
    @staticmethod
    def _remove_sql_comments(query: str) -> str:
        """Remove SQL comments (-- and /* */)"""
        # Remove single-line comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        # Remove multi-line comments
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        return query
    
    @staticmethod
    def _strip_explanations(query: str) -> str:
        """Strip explanatory text before/after the query"""
        lines = query.split('\n')
        
        # Find first line that looks like SQL
        sql_keywords = ['SELECT', 'WITH', 'EXPLAIN', 'DESCRIBE', 'SHOW']
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip().upper()
            if any(stripped.startswith(kw) for kw in sql_keywords):
                start_idx = i
                break
        
        # Find last line that ends SQL (ends with ; or is last statement)
        end_idx = len(lines)
        for i in range(len(lines) - 1, start_idx - 1, -1):
            line = lines[i].strip()
            if line and not line.startswith('--'):
                end_idx = i + 1
                break
        
        return '\n'.join(lines[start_idx:end_idx])
    
    @staticmethod
    def _validate_sql_format(query: str) -> bool:
        """Basic SQL format validation"""
        if not query:
            return False
        
        query_upper = query.upper().strip()
        
        # Must start with allowed keywords
        allowed_starts = ['SELECT', 'WITH', 'EXPLAIN', 'DESCRIBE', 'SHOW']
        if not any(query_upper.startswith(kw) for kw in allowed_starts):
            return False
        
        # Should contain FROM or a valid structure
        if 'SELECT' in query_upper and 'FROM' not in query_upper:
            # Exception for SELECT without FROM (e.g., SELECT 1)
            if not re.search(r'SELECT\s+\d+', query_upper):
                return False
        
        return True
    
    @staticmethod
    def add_limit_if_missing(query: str, default_limit: int = 100) -> str:
        """Add LIMIT clause if not present"""
        query_upper = query.upper()
        
        # Check if LIMIT already exists
        if 'LIMIT' in query_upper:
            return query
        
        # Check if it's a SELECT statement
        if not query_upper.strip().startswith('SELECT'):
            return query
        
        # Add LIMIT before any trailing semicolon
        if query.rstrip().endswith(';'):
            query = query.rstrip()[:-1]
            query = f"{query} LIMIT {default_limit};"
        else:
            query = f"{query} LIMIT {default_limit}"
        
        return query
    
    @staticmethod
    def normalize_query(query: str, db_type: str) -> str:
        """Normalize query formatting"""
        if db_type == "postgresql":
            # Ensure proper spacing
            query = re.sub(r'\s+', ' ', query)
            # Uppercase keywords
            keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 
                       'OUTER', 'ON', 'GROUP', 'BY', 'ORDER', 'LIMIT', 'OFFSET',
                       'AND', 'OR', 'NOT', 'NULL', 'AS', 'DISTINCT', 'UNION', 'ALL']
            for kw in keywords:
                query = re.sub(rf'\b{kw}\b', kw, query, flags=re.IGNORECASE)
        
        return query.strip()

# Convenience functions
def clean_query(raw_query: str, db_type: str) -> Tuple[str, bool]:
    """Clean query based on database type"""
    cleaner = QueryCleaner()
    
    if db_type == "postgresql":
        return cleaner.clean_sql_query(raw_query)
    elif db_type == "mongodb":
        return cleaner.clean_mongodb_query(raw_query)
    else:
        return raw_query, False
