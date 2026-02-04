"""
Security Module - Defense-in-Depth Strategy
Multi-layer security for database access
"""

from typing import Dict, Any, List, Set, Optional
from functools import wraps
import logging
import hashlib
import re

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Defense-in-depth security manager
    
    Layers:
    1. Connection Level: Read-only database users
    2. Application Level: AST validation + keyword filtering
    3. Data Level: PII redaction
    4. Access Control: Row-level security
    """
    
    # Dangerous SQL patterns (injection detection)
    SQL_INJECTION_PATTERNS = [
        r';\s*DROP\s+',
        r';\s*DELETE\s+',
        r';\s*UPDATE\s+',
        r';\s*INSERT\s+',
        r'UNION\s+SELECT',
        r'OR\s+1\s*=\s*1',
        r'OR\s+\'\w+\'\s*=\s*\'\w+\'',
        r'--\s*$',
        r'/\*.*?\*/',
        r'xp_cmdshell',
        r'exec\s*\(',
        r'EXEC\s*\(',
    ]
    
    # System tables to block
    FORBIDDEN_TABLES = {
        'pg_catalog', 'information_schema', 'mysql', 'sys',
        'sqlite_master', 'sqlite_temp_master'
    }
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) 
                                 for p in self.SQL_INJECTION_PATTERNS]
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent injection
        """
        if not user_input:
            return ""
        
        # Remove null bytes
        sanitized = user_input.replace('\x00', '')
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def check_sql_injection(self, query: str) -> tuple[bool, List[str]]:
        """
        Check for SQL injection patterns
        
        Returns:
            (is_safe, list_of_detected_patterns)
        """
        detected = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(query):
                detected.append(self.SQL_INJECTION_PATTERNS[i])
        
        is_safe = len(detected) == 0
        return is_safe, detected
    
    def validate_table_access(self, tables: List[str], 
                             allowed_tables: Optional[Set[str]] = None) -> bool:
        """
        Validate that tables are in whitelist and not system tables
        """
        if allowed_tables is None:
            # If no whitelist, just check for system tables
            allowed_tables = set()
        
        for table in tables:
            # Check if system table
            if any(forbidden in table.lower() for forbidden in self.FORBIDDEN_TABLES):
                logger.warning(f"Access to system table blocked: {table}")
                return False
            
            # Check whitelist if provided
            if allowed_tables and table.lower() not in {t.lower() for t in allowed_tables}:
                logger.warning(f"Access to unauthorized table blocked: {table}")
                return False
        
        return True
    
    def generate_read_only_connection_string(self, 
                                             original_connection_string: str,
                                             db_type: str) -> str:
        """
        Generate a read-only connection string
        
        This is a placeholder - in production, you'd:
        1. Create a dedicated read-only user in the database
        2. Return connection string with that user
        """
        # For now, return the original with a flag
        # In production, implement actual read-only user creation
        logger.info("Using connection string (ensure DB user is read-only)")
        return original_connection_string
    
    def audit_log(self, action: str, user_id: int, connection_id: int,
                 query: str, success: bool, error: str = None):
        """
        Log security-relevant actions
        """
        log_entry = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                'name', logging.INFO, '', 0, '', (), None
            )),
            "action": action,
            "user_id": user_id,
            "connection_id": connection_id,
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
            "success": success,
            "error": error
        }
        
        if success:
            logger.info(f"AUDIT: {log_entry}")
        else:
            logger.warning(f"AUDIT: {log_entry}")
    
    def mask_connection_string(self, connection_string: str) -> str:
        """
        Mask sensitive info in connection string for logging
        """
        # Mask password
        masked = re.sub(r':([^:@]+)@', ':****@', connection_string)
        return masked

class RateLimiter:
    """
    Simple rate limiter for API endpoints
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> list of timestamps
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed under rate limit"""
        import time
        
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Get user's request history
        user_requests = self.requests.get(user_id, [])
        
        # Filter to current window
        recent_requests = [t for t in user_requests if t > window_start]
        
        # Check limit
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Update requests
        recent_requests.append(current_time)
        self.requests[user_id] = recent_requests
        
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests in window"""
        import time
        
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        user_requests = self.requests.get(user_id, [])
        recent_requests = [t for t in user_requests if t > window_start]
        
        return max(0, self.max_requests - len(recent_requests))

def require_permissions(*permissions):
    """Decorator to require specific permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In production, check user permissions here
            # For now, allow all authenticated users
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get or create security manager singleton"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
