"""
Comprehensive Test Suite for Enhanced RAG Application
Tests all new features and components
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.utils.query_cleaner import QueryCleaner, clean_query
from app.services.query_validator import QueryValidator, validate_query
from app.services.schema_store import SchemaStore
from app.services.pii_redaction import PIIRedactor, SimplePIIRedactor
from app.services.visualizer import Visualizer, ChartType
from app.agents.sql_agent import SQLAgent
from app.core.security import SecurityManager
from app.core.prompts import get_query_generation_prompt

# Test Query Cleaner
class TestQueryCleaner:
    def test_extract_from_markdown_code_block(self):
        raw = "```sql\nSELECT * FROM users;\n```"
        cleaned, valid = clean_query(raw, "postgresql")
        assert "SELECT * FROM users" in cleaned
        assert valid is True
    
    def test_remove_sql_comments(self):
        raw = "SELECT * FROM users -- get all users\nWHERE id = 1;"
        cleaner = QueryCleaner()
        cleaned = cleaner._remove_sql_comments(raw)
        assert "--" not in cleaned
        assert "SELECT * FROM users" in cleaned
    
    def test_add_limit_if_missing(self):
        query = "SELECT * FROM users"
        cleaner = QueryCleaner()
        result = cleaner.add_limit_if_missing(query, 100)
        assert "LIMIT 100" in result
    
    def test_validate_sql_format(self):
        cleaner = QueryCleaner()
        assert cleaner._validate_sql_format("SELECT * FROM users") is True
        assert cleaner._validate_sql_format("DROP TABLE users") is False
        assert cleaner._validate_sql_format("") is False

# Test Query Validator
class TestQueryValidator:
    def test_validate_safe_select(self):
        validator = QueryValidator()
        result = validator.validate("SELECT * FROM users", "postgresql")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_forbidden_operation(self):
        validator = QueryValidator()
        result = validator.validate("DELETE FROM users", "postgresql")
        assert result.is_valid is False
        assert any("DELETE" in err for err in result.errors)
    
    def test_validate_sql_injection(self):
        validator = QueryValidator()
        result = validator.validate("SELECT * FROM users; DROP TABLE users;", "postgresql")
        assert result.is_valid is False
        assert any("injection" in err.lower() for err in result.errors)
    
    def test_validate_table_whitelist(self):
        validator = QueryValidator(allowed_tables={"users", "orders"})
        result = validator.validate("SELECT * FROM products", "postgresql")
        assert result.is_valid is False
        assert any("products" in err for err in result.errors)
    
    def test_is_read_only(self):
        validator = QueryValidator()
        assert validator.is_read_only("SELECT * FROM users") is True
        assert validator.is_read_only("INSERT INTO users VALUES (1)") is False

# Test Schema Store
class TestSchemaStore:
    @patch('app.services.schema_store.OpenAIEmbeddings')
    @patch('app.services.schema_store.PGVector')
    def test_create_table_description(self, mock_pgvector, mock_embeddings):
        store = SchemaStore()
        columns = [
            {"name": "id", "type": "integer", "primary_key": True},
            {"name": "email", "type": "varchar", "nullable": False},
            {"name": "user_id", "type": "integer", "foreign_key": {"referred_table": "users", "referred_columns": ["id"]}}
        ]
        
        desc = store._create_table_description("customers", columns, "postgresql")
        assert "Table: customers" in desc
        assert "id (integer) [PRIMARY KEY]" in desc
        assert "user_id (integer) [FOREIGN KEY]" in desc

# Test PII Redaction
class TestPIIRedaction:
    def test_redact_email(self):
        redactor = SimplePIIRedactor()
        text = "Contact john@example.com for support"
        result = redactor.redact_text(text)
        assert "[EMAIL_ADDRESS]" in result
        assert "john@example.com" not in result
    
    def test_redact_phone(self):
        redactor = SimplePIIRedactor()
        text = "Call 555-123-4567 for help"
        result = redactor.redact_text(text)
        assert "[PHONE_NUMBER]" in result
    
    def test_redact_results(self):
        redactor = SimplePIIRedactor()
        results = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@test.com"}
        ]
        redacted = redactor.redact_results(results)
        assert all("[EMAIL_ADDRESS]" in str(r.get("email", "")) for r in redacted)

# Test Visualizer
class TestVisualizer:
    def test_recommend_line_chart_for_time_series(self):
        visualizer = Visualizer()
        results = [
            {"date": "2024-01-01", "sales": 100},
            {"date": "2024-01-02", "sales": 150},
            {"date": "2024-01-03", "sales": 200}
        ]
        
        rec = visualizer.recommend_visualization(results, "Show sales over time")
        assert rec.chart_type == ChartType.LINE
    
    def test_recommend_bar_chart_for_categories(self):
        visualizer = Visualizer()
        results = [
            {"category": "A", "count": 10},
            {"category": "B", "count": 20},
            {"category": "C", "count": 15}
        ]
        
        rec = visualizer.recommend_visualization(results, "Count by category")
        assert rec.chart_type == ChartType.BAR
    
    def test_generate_plotly_config(self):
        visualizer = Visualizer()
        results = [{"x": 1, "y": 10}, {"x": 2, "y": 20}]
        rec = visualizer.recommend_visualization(results)
        
        config = visualizer.generate_plotly_config(rec, results)
        assert "data" in config
        assert "layout" in config

# Test Security Manager
class TestSecurityManager:
    def test_sanitize_input(self):
        manager = SecurityManager()
        dirty = "Hello\x00World<script>"
        clean = manager.sanitize_input(dirty)
        assert "\x00" not in clean
        assert "<script>" not in clean
    
    def test_check_sql_injection(self):
        manager = SecurityManager()
        safe, detected = manager.check_sql_injection("SELECT * FROM users")
        assert safe is True
        assert len(detected) == 0
        
        safe, detected = manager.check_sql_injection("SELECT * FROM users; DROP TABLE users;")
        assert safe is False
        assert len(detected) > 0
    
    def test_validate_table_access(self):
        manager = SecurityManager()
        assert manager.validate_table_access(["users"], {"users", "orders"}) is True
        assert manager.validate_table_access(["admin"], {"users"}) is False
        assert manager.validate_table_access(["pg_catalog.users"]) is False

# Test Prompts
class TestPrompts:
    def test_get_query_generation_prompt_postgresql(self):
        schema = {"users": [{"name": "id", "type": "integer"}]}
        prompt = get_query_generation_prompt("postgresql", json.dumps(schema), "Show all users")
        
        assert "EXAMPLES:" in prompt
        assert "users" in prompt
        assert "CRITICAL RULES:" in prompt
        assert "SELECT" in prompt
    
    def test_get_query_generation_prompt_mongodb(self):
        schema = {"users": [{"name": "id", "type": "ObjectId"}]}
        prompt = get_query_generation_prompt("mongodb", json.dumps(schema), "Find all users")
        
        assert "EXAMPLES:" in prompt
        assert "MongoDB" in prompt or "mongodb" in prompt

# Test SQL Agent (with mocking)
class TestSQLAgent:
    @patch('app.agents.sql_agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm):
        agent = SQLAgent({"provider": "openai", "api_key": "test-key"})
        assert agent.provider == "openai"
        assert agent.workflow is not None

# Integration Tests
class TestIntegration:
    def test_full_query_pipeline_mock(self):
        """Test the complete query pipeline with mocks"""
        # This would test the full flow: user query -> schema retrieval -> 
        # query generation -> validation -> execution -> visualization
        pass

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
