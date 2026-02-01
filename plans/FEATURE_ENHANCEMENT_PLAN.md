# Feature Enhancement Plan

## Overview
This document outlines the planned enhancements for the SaaS RAG application based on user requirements.

---

## 1. Auto-Execute Read-Only Queries

### Current Behavior
- LLM generates SQL query suggestions in text format
- User sees the query but results are not automatically fetched

### Desired Behavior
- When LLM generates a query, automatically execute it
- Display both the query AND the actual results to the user
- Ensure ONLY read-only operations are allowed (SELECT, SHOW, DESCRIBE)

### Implementation Plan

#### Backend Changes
1. **Create Query Safety Validator** (`backend/app/services/query_validator.py`)
   - Parse SQL queries to detect operation type
   - Whitelist: SELECT, SHOW, DESCRIBE, EXPLAIN
   - Blacklist: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE
   - Support for multiple SQL dialects (PostgreSQL, MySQL, MongoDB)

2. **Modify RAG Service** (`backend/app/services/rag_service_local.py`)
   - Add method `execute_safe_query(query_string, connection)`
   - Execute only if query passes safety check
   - Return results in structured format
   - Limit result rows (e.g., max 100) to prevent memory issues

3. **Update Query API** (`backend/app/api/query.py`)
   - Add parameter: `auto_execute: bool = True`
   - When LLM generates query, automatically validate and execute
   - Return `query_results` populated with actual data
   - Add execution metadata (row count, execution time)

#### Frontend Changes
1. **Update ChatInterface** (`frontend/src/components/ChatInterface.js`)
   - Display query results in a formatted table/grid
   - Show row count and execution time
   - Add "View as Table" toggle for results
   - Handle large result sets with pagination

### Safety Measures
```python
READ_ONLY_KEYWORDS = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'WITH']
FORBIDDEN_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 
                      'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE']

# Additional safety: Use read-only database user
# Create a separate DB user with only SELECT permissions
```

---

## 2. LLM Provider Switching with API Key Management

### Current Behavior
- Fixed to local Ollama models
- No option to use cloud providers

### Desired Behavior
- User can switch between Local (Ollama) and Cloud providers
- Support for: OpenAI, Google Gemini, OpenRouter
- Per-user API key storage (encrypted)
- Dynamic model selection based on provider

### Implementation Plan

#### Database Schema Changes
```sql
-- New table for user LLM settings
CREATE TABLE user_llm_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    provider VARCHAR(50) NOT NULL, -- 'ollama', 'openai', 'gemini', 'openrouter'
    api_key_encrypted TEXT, -- Encrypted API key
    model_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Backend Changes

1. **Create LLM Provider Factory** (`backend/app/services/llm_factory.py`)
   ```python
   class LLMProviderFactory:
       @staticmethod
       def get_provider(provider_type: str, config: dict):
           if provider_type == 'ollama':
               return OllamaProvider(config)
           elif provider_type == 'openai':
               return OpenAIProvider(config)
           elif provider_type == 'gemini':
               return GeminiProvider(config)
           elif provider_type == 'openrouter':
               return OpenRouterProvider(config)
   ```

2. **Create Provider Classes** (`backend/app/services/llm_providers/`)
   - `base_provider.py` - Abstract base class
   - `ollama_provider.py` - Local Ollama
   - `openai_provider.py` - OpenAI GPT models
   - `gemini_provider.py` - Google Gemini
   - `openrouter_provider.py` - OpenRouter (supports multiple models)

3. **Update Settings API** (`backend/app/api/settings.py`)
   - Add endpoints:
     - `POST /api/settings/llm` - Save LLM configuration
     - `GET /api/settings/llm` - Get user's LLM configuration
     - `GET /api/settings/llm/models` - Get available models for provider
     - `POST /api/settings/llm/validate` - Validate API key

4. **Encryption for API Keys**
   - Use Fernet symmetric encryption
   - Store encryption key in environment variable
   - Never return decrypted keys to frontend

#### Frontend Changes

1. **Enhanced LLMSettings Component** (`frontend/src/components/LLMSettings.js`)
   - Provider selection dropdown (Ollama, OpenAI, Gemini, OpenRouter)
   - API key input (password field with show/hide)
   - Model selection dropdown (dynamic based on provider)
   - "Test Connection" button
   - Save/Update configuration

2. **Provider-Specific UI**
   - **OpenAI/Gemini**: Show predefined model list
   - **OpenRouter**: Allow custom model name input + fetch available models
   - **Ollama**: Show locally available models

---

## 3. Dynamic Model Fetching

### OpenAI
```python
# Fetch models from OpenAI API
import openai
client = openai.OpenAI(api_key=user_key)
models = client.models.list()
# Filter for GPT models only
```

### Google Gemini
```python
# Gemini has fixed model list
GEMINI_MODELS = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-1.0-pro'
]
```

### OpenRouter
```python
# Fetch from OpenRouter API
import requests
response = requests.get(
    'https://openrouter.ai/api/v1/models',
    headers={'Authorization': f'Bearer {api_key}'}
)
models = response.json()['data']
```

### Ollama (Local)
```python
# Fetch from local Ollama
docker exec ollama ollama list
```

---

## 4. Performance Optimization

### Current Issue
- 2-minute response time for local LLM on CPU

### Optimization Strategies

#### Option 1: Use Faster/Lighter Models
- Switch from `llama3.2` to `phi3` or `tinyllama`
- Trade-off: Slightly lower quality for much faster responses

#### Option 2: Response Streaming
- Implement Server-Sent Events (SSE) for streaming responses
- User sees text appearing gradually instead of waiting

#### Option 3: Query Result Caching
- Cache frequent query results
- Return cached results for identical queries

#### Option 4: Async Processing
- For long-running queries, return job ID immediately
- Poll for results or use WebSockets

#### Option 5: GPU Instance (Recommended for Production)
- Upgrade to AWS g4dn.xlarge or similar with GPU
- 10-50x faster inference for local models

---

## 5. Enhanced Response Presentation

### Query Results Display
- Format results as sortable/filterable table
- Support for JSON view for nested data
- Export results to CSV/JSON
- Syntax highlighting for SQL queries

### Response Layout
```
┌─────────────────────────────────────┐
│ 🤖 AI Response                      │
│ Natural language explanation        │
├─────────────────────────────────────┤
│ 📝 Generated Query                  │
│ [SQL with syntax highlighting]      │
│ [Copy] [Download] buttons           │
├─────────────────────────────────────┤
│ 📊 Query Results (42 rows, 0.3s)    │
│ [Sortable table with pagination]    │
│ [Export CSV] [Export JSON]          │
└─────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1: Critical (Immediate)
1. ✅ Fix existing bugs (completed)
2. Auto-execute read-only queries with safety
3. Basic LLM provider switching (Local/OpenAI)

### Phase 2: High Priority
4. Response streaming for better UX
5. Enhanced results presentation (tables)
6. Support for Gemini and OpenRouter

### Phase 3: Nice to Have
7. Query result caching
8. Export functionality
9. Advanced query visualization

---

## Files to Modify

### Backend
- `backend/app/services/query_validator.py` (NEW)
- `backend/app/services/llm_factory.py` (NEW)
- `backend/app/services/llm_providers/` (NEW DIRECTORY)
- `backend/app/services/rag_service_local.py`
- `backend/app/api/query.py`
- `backend/app/api/settings.py`
- `backend/app/models/database.py`

### Frontend
- `frontend/src/components/LLMSettings.js`
- `frontend/src/components/ChatInterface.js`
- `frontend/src/api/client.js`
- `frontend/src/components/QueryResultsTable.js` (NEW)

---

## Security Considerations

1. **API Key Storage**: Encrypt at rest, never expose in frontend
2. **Query Safety**: Multi-layer validation (keyword check + read-only DB user)
3. **Rate Limiting**: Prevent API abuse for cloud providers
4. **Input Sanitization**: Prevent SQL injection in generated queries

---

Would you like me to proceed with implementing these features? I recommend starting with Phase 1 (auto-execute queries and basic provider switching).