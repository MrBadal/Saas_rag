Base URL: `http://localhost:8000` (development)

## Authentication

All endpoints except `/api/auth/*` require Bearer token authentication.

**Header:**
```
Authorization: Bearer <your_token>
```

## Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### POST `/api/auth/login`
Login existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

### Connections

#### GET `/api/connections/`
Get all database connections for the authenticated user.

**Response:**
```json
{
  "connections": [
    {
      "id": 1,
      "name": "Production DB",
      "db_type": "postgresql",
      "metadata": {
        "tables": ["users", "orders"]
      }
    }
  ]
}
```

#### POST `/api/connections/`
Create a new database connection.

**Request:**
```json
{
  "name": "Production DB",
  "db_type": "postgresql",  // or "mongodb"
  "connection_string": "postgresql://user:pass@host:port/dbname"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Production DB",
  "db_type": "postgresql",
  "metadata": {
    "tables": ["users", "orders"]
  }
}
```

#### GET `/api/connections/{connection_id}/schema`
Get the schema for a specific connection.

**Response:**
```json
{
  "schema": {
    "users": [
      {"name": "id", "type": "INTEGER"},
      {"name": "email", "type": "VARCHAR"}
    ]
  }
}
```

---

### Query

#### POST `/api/query/`
Execute a natural language query.

**Request:**
```json
{
  "connection_id": 1,
  "query": "Show me all users who signed up last week"
}
```

**Response:**
```json
{
  "answer": "Here are the users who signed up last week...",
  "generated_query": "SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'",
  "query_results": [
    {"id": 1, "email": "user1@example.com"}
  ]
}
```

---

### User Settings

#### GET `/api/settings/`
Get current user settings.

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo"
}
```

#### POST `/api/settings/`
Update user settings.

**Request:**
```json
{
  "llm_provider": "openai",  // or "gemini", "anthropic"
  "llm_api_key": "sk-...",
  "llm_model": "gpt-3.5-turbo"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo",
  "message": "Settings updated successfully"
}
```

#### POST `/api/settings/test-api-key`
Test if the API key is valid.

**Request:**
```json
{
  "llm_provider": "openai",
  "llm_api_key": "sk-...",
  "llm_model": "gpt-3.5-turbo"
}
```

**Response (Success):**
```json
{
  "valid": true,
  "message": "API key is valid"
}
```

**Response (Error):**
```json
{
  "valid": false,
  "message": "Invalid API key: ..."
}
```

---

## Supported LLM Providers

| Provider | Models | API Key Source |
|----------|--------|----------------|
| OpenAI | gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview | User Settings |
| Google Gemini | gemini-pro, gemini-pro-vision | User Settings |
| Anthropic Claude | claude-3-opus-20240229, claude-3-sonnet-20240229 | User Settings |
| OpenRouter | All OpenRouter models | User Settings |

The API key in user settings takes precedence over the global API key in `.env`.

