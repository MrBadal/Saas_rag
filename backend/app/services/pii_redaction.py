"""
PII Detection and Redaction Service
Uses Microsoft Presidio for enterprise-grade data protection
"""

from typing import List, Dict, Any, Optional, Set
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import logging

logger = logging.getLogger(__name__)

class PIIRedactor:
    """
    PII detection and redaction using Microsoft Presidio
    
    Protects sensitive data before sending to LLM
    Ensures compliance with GDPR, HIPAA, etc.
    """
    
    # Default PII entities to detect
    DEFAULT_ENTITIES = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "US_SSN",
        "US_BANK_NUMBER",
        "IBAN_CODE",
        "IP_ADDRESS",
        "PERSON",
        "LOCATION",
        "DATE_TIME"
    ]
    
    # Redaction operators
    REDACTION_OPERATORS = {
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CREDIT_CARD]"}),
        "US_SSN": OperatorConfig("replace", {"new_value": "[SSN]"}),
        "US_BANK_NUMBER": OperatorConfig("replace", {"new_value": "[BANK_ACCOUNT]"}),
        "IBAN_CODE": OperatorConfig("replace", {"new_value": "[IBAN]"}),
        "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[IP_ADDRESS]"}),
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATE]"}),
        "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})
    }
    
    def __init__(self, language: str = "en", entities: Optional[List[str]] = None):
        """
        Initialize PII redactor
        
        Args:
            language: Language for analysis (default: "en")
            entities: List of PII entities to detect (default: all)
        """
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            self.language = language
            self.entities = entities or self.DEFAULT_ENTITIES
            logger.info("PIIRedactor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            self.analyzer = None
            self.anonymizer = None
    
    def redact_text(self, text: str) -> str:
        """
        Redact PII from text
        
        Args:
            text: Input text
            
        Returns:
            Text with PII redacted
        """
        if not self.analyzer or not text:
            return text
        
        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=self.entities
            )
            
            if not results:
                return text
            
            # Anonymize detected entities
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=self.REDACTION_OPERATORS
            )
            
            return anonymized.text
            
        except Exception as e:
            logger.error(f"Redaction failed: {e}")
            return text
    
    def redact_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Redact PII from query results
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Results with PII redacted
        """
        if not self.analyzer or not results:
            return results
        
        redacted_results = []
        
        for row in results:
            redacted_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    redacted_row[key] = self.redact_text(value)
                else:
                    redacted_row[key] = value
            redacted_results.append(redacted_row)
        
        return redacted_results
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text without redacting
        
        Returns:
            List of detected PII entities
        """
        if not self.analyzer or not text:
            return []
        
        try:
            results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=self.entities
            )
            
            return [
                {
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end]
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return []
    
    def has_pii(self, text: str) -> bool:
        """Quick check if text contains PII"""
        return len(self.detect_pii(text)) > 0
    
    def redact_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PII from schema metadata (column names, sample data)
        """
        if not self.analyzer:
            return schema
        
        redacted_schema = {}
        
        for table_name, columns in schema.items():
            # Check if table name contains PII
            redacted_table_name = self.redact_text(table_name)
            
            if isinstance(columns, list):
                redacted_columns = []
                for col in columns:
                    redacted_col = col.copy()
                    if 'name' in col:
                        redacted_col['name'] = self.redact_text(col['name'])
                    redacted_columns.append(redacted_col)
                redacted_schema[redacted_table_name] = redacted_columns
            else:
                redacted_schema[redacted_table_name] = columns
        
        return redacted_schema
    
    def get_stats(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get PII detection statistics from results
        
        Returns:
            Dict with entity type counts
        """
        stats = {}
        
        for row in results:
            for value in row.values():
                if isinstance(value, str):
                    detected = self.detect_pii(value)
                    for entity in detected:
                        entity_type = entity["entity_type"]
                        stats[entity_type] = stats.get(entity_type, 0) + 1
        
        return stats

class SimplePIIRedactor:
    """
    Lightweight PII redactor using regex patterns
    Fallback when Presidio is not available
    """
    
    PATTERNS = {
        'EMAIL_ADDRESS': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE_NUMBER': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'CREDIT_CARD': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'US_SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    }
    
    def __init__(self):
        import re
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, pattern in self.PATTERNS.items()
        }
    
    def redact_text(self, text: str) -> str:
        """Redact PII using regex patterns"""
        if not text:
            return text
        
        redacted = text
        for entity_type, pattern in self.compiled_patterns.items():
            redacted = pattern.sub(f'[{entity_type}]', redacted)
        
        return redacted
    
    def redact_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Redact PII from results"""
        redacted_results = []
        
        for row in results:
            redacted_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    redacted_row[key] = self.redact_text(value)
                else:
                    redacted_row[key] = value
            redacted_results.append(redacted_row)
        
        return redacted_results

# Factory function
def create_redactor(use_presidio: bool = True) -> PIIRedactor:
    """Create PII redactor"""
    if use_presidio:
        redactor = PIIRedactor()
        if redactor.analyzer:
            return redactor
    
    # Fallback to simple redactor
    logger.info("Using simple regex-based PII redactor")
    return SimplePIIRedactor()
