# ⚙️ Technical Documentation

This document provides comprehensive technical details about the DataQuery AI platform architecture, code organization, API reference, and development guidelines.

---

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Code Organization](#code-organization)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [RAG Implementation](#rag-implementation)
- [Authentication Flow](#authentication-flow)
- [Frontend Architecture](#frontend-architecture)
- [Development Guidelines](#development-guidelines)
- [Deployment Architecture](#deployment-architecture)

---

## System Architecture

### High-Level Overview

```mermaid
flowchart TB
    subgraph Client["🖥️ Client Layer"]
        Browser["Web Browser"]
    end

    subgraph Frontend["⚛️ Frontend (React)"]
        Components["React Components"]
        APIClient["API Client (Axios)"]
    end

    subgraph Backend["🚀 Backend (FastAPI)"]
        API["API Routes"]
        Auth["Authentication"]
        Services["Services Layer"]
    end

    subgraph AI["🤖 AI Layer"]
        RAG["RAG Service"]
        Embeddings["OpenAI Embeddings"]
        LLM["LLM Integration"]
    end

    subgraph Data["🗄️ Data Layer"]
        PG[(PostgreSQL + pgvector)]
        UserDB[(User Databases)]
    end

    Browser --> Components
    Components --> APIClient
    APIClient --> API
    API --> Auth
    API --> Services
    Services --> RAG
    RAG --> Embeddings
    RAG --> LLM
    Services --> PG
    Services --> UserDB
```

### Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend API
    participant R as RAG Service
    participant L as LLM Provider
    participant D as Database

    U->>F: Type natural language query
    F->>B: POST /api/query/ {query, connection_id}
    B->>D: Fetch connection details
    B->>R: Process query with RAG
    R->>D: Retrieve vector context
    R->>L: Send prompt with context
    L->>R: Return generated response
    R->>B: Return answer + query
    B->>D: Save to query history
    B->>F: Return response
    F->>U: Display answer & results
```

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.115.0 | High-performance API framework |
| **Server** | Uvicorn | 0.32.0 | ASGI server |
| **ORM** | SQLAlchemy | 2.0.36 | Database ORM |
| **Validation** | Pydantic | 2.9.2 | Data validation |
| **RAG Framework** | LangChain | 0.3.0 | LLM orchestration |
| **Embeddings** | OpenAI | Latest | Vector embeddings |
| **Vector DB** | pgvector | 0.2.5 | Vector similarity search |
| **Auth** | python-jose | 3.3.0 | JWT tokens |
| **Password Hashing** | bcrypt | Latest | Secure password storage |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.2.0 | UI library |
| **Build Tool** | Create React App | 5.0.1 | Build system |
| **Styling** | TailwindCSS | 3.4.1 | Utility-first CSS |
| **HTTP Client** | Axios | 1.6.5 | API requests |
| **Routing** | React Router | 6.21.3 | Client-side routing |
| **Icons** | Heroicons | Latest | SVG icons |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application containers |
| **Orchestration** | Docker Compose | Local development |
| **Database** | PostgreSQL 16 | Primary data store |
| **Vector Extension** | pgvector | Vector storage |
| **Cloud** | AWS ECS | Production deployment |

---

## Code Organization

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── connections.py     # Database connection management
│   │   ├── query.py           # Query execution endpoints
│   │   └── settings.py        # User settings management
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   └── config.py          # Settings & environment
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   └── database.py        # SQLAlchemy models
│   └── services/               # Business logic
│       ├── __init__.py
│       ├── connectors.py      # Database connectors
│       └── rag_service.py     # RAG implementation
├── Dockerfile
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   └── client.js          # API client configuration
│   ├── components/            # React components
│   │   ├── Login.js          # Authentication UI
│   │   ├── Dashboard.js      # Main dashboard
│   │   ├── ChatInterface.js  # Chat/query interface
│   │   ├── Connections.js    # Connection management
│   │   └── Settings.js       # User settings
│   ├── App.js                # Main app component
│   ├── index.css             # Global styles
│   └── index.js              # Entry point
├── Dockerfile
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

---

## API Reference

### Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com
```

### Authentication

All endpoints except `/api/auth/*` require Bearer token authentication.

**Header Format:**
```http
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### Authentication

##### POST `/api/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid email format

---

##### POST `/api/auth/login`
Authenticate existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials

---

#### Connections

##### GET `/api/connections/`
List all database connections for the authenticated user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Production PostgreSQL",
    "db_type": "postgresql",
    "metadata": {
      "schema": {
        "users": [
          {"name": "id", "type": "INTEGER"},
          {"name": "email", "type": "VARCHAR"}
        ]
      }
    }
  }
]
```

---

##### POST `/api/connections/`
Create a new database connection.

**Request:**
```json
{
  "name": "Production DB",
  "db_type": "postgresql",
  "connection_string": "postgresql://user:pass@host:5432/dbname"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Production DB",
  "db_type": "postgresql",
  "metadata": {
    "schema": {
      "users": [{"name": "id", "type": "INTEGER"}]
    }
  }
}
```

**Process:**
1. Validates connection string format
2. Tests database connectivity
3. Extracts schema information
4. Creates vector embeddings for RAG
5. Stores encrypted connection details

**Error Responses:**
- `400 Bad Request`: Invalid connection string or connection failed
- `409 Conflict`: Connection with same name already exists

---

##### DELETE `/api/connections/{id}`
Delete a database connection.

**Response (200 OK):**
```json
{
  "message": "Connection deleted successfully"
}
```

---

#### Query

##### POST `/api/query/`
Execute a natural language query.

**Request:**
```json
{
  "connection_id": 1,
  "query": "Show me top 10 customers by revenue"
}
```

**Response (200 OK):**
```json
{
  "answer": "The top 10 customers by revenue are: 1. Acme Corp ($125,000)...",
  "generated_query": "SELECT customer_name, SUM(amount) as revenue FROM...",
  "query_results": [
    {"customer_name": "Acme Corp", "revenue": 125000},
    {"customer_name": "TechStart", "revenue": 98000}
  ]
}
```

**Process:**
1. Retrieves vector store for the connection
2. Performs semantic search for relevant context
3. Constructs prompt with context + user query
4. Calls LLM to generate response
5. Optionally generates and executes database query
6. Saves to query history

---

##### GET `/api/query/history`
Get query history for the authenticated user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "query": "Show me all users",
    "response": "There are 1,234 users in the database...",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### Settings

##### GET `/api/settings/`
Get current user settings.

**Response (200 OK):**
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo",
  "has_api_key": true,
  "key_last_updated": "2024-01-15T10:30:00Z"
}
```

---

##### POST `/api/settings/`
Update user settings.

**Request:**
```json
{
  "llm_provider": "openai",
  "llm_api_key": "sk-...",
  "llm_model": "gpt-4"
}
```

**Response (200 OK):**
```json
{
  "message": "Settings updated successfully"
}
```

---

##### GET `/api/settings/providers`
Get available LLM providers and models.

**Response (200 OK):**
```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "models": [
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
      ]
    },
    {
      "id": "openrouter",
      "name": "OpenRouter",
      "models": [
        {"id": "openai/gpt-4", "name": "GPT-4 via OpenRouter"}
      ]
    }
  ]
}
```

---

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ DATABASE_CONNECTION : has
    USER ||--o{ QUERY_HISTORY : creates
    USER ||--|| USER_SETTINGS : has
    DATABASE_CONNECTION ||--o{ QUERY_HISTORY : generates

    USER {
        int id PK
        string email UK
        string hashed_password
        datetime created_at
    }

    USER_SETTINGS {
        int id PK
        int user_id FK
        string llm_provider
        text llm_api_key
        string llm_model
        datetime created_at
        datetime updated_at
    }

    DATABASE_CONNECTION {
        int id PK
        int user_id FK
        string name
        string db_type
        text connection_string
        json db_metadata
        datetime created_at
    }

    QUERY_HISTORY {
        int id PK
        int user_id FK
        int connection_id FK
        text query
        text response
        datetime created_at
    }
```

### Table Definitions

#### `users`
Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |

#### `user_settings`
Stores user preferences and LLM configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | UNIQUE, FOREIGN KEY | Reference to users table |
| `llm_provider` | VARCHAR(50) | DEFAULT 'openai' | LLM provider name |
| `llm_api_key` | TEXT | NULLABLE | Encrypted API key |
| `llm_model` | VARCHAR(100) | DEFAULT 'gpt-3.5-turbo' | Model identifier |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | ON UPDATE | Last modification time |

#### `database_connections`
Stores database connection configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY, INDEX | Reference to users table |
| `name` | VARCHAR(255) | NOT NULL | Connection display name |
| `db_type` | VARCHAR(50) | NOT NULL | 'postgresql' or 'mongodb' |
| `connection_string` | TEXT | NOT NULL | Encrypted connection URL |
| `db_metadata` | JSON | NULLABLE | Schema and metadata |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### `query_history`
Stores query execution history.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY, INDEX | Reference to users table |
| `connection_id` | INTEGER | FOREIGN KEY | Reference to connection |
| `query` | TEXT | NOT NULL | User's natural language query |
| `response` | TEXT | NOT NULL | AI-generated response |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Query execution time |

### pgvector Collections

Vector embeddings are stored in pgvector with the following naming convention:

```
collection_name: "connection_{connection_id}"
```

Each collection contains:
- **Documents**: Schema descriptions and sample data
- **Embeddings**: 1536-dimensional vectors (OpenAI text-embedding-ada-002)
- **Metadata**: Source table, column info, timestamps

---

## RAG Implementation

### Overview

The RAG (Retrieval-Augmented Generation) system enhances LLM responses by retrieving relevant context from the database schema and sample data before generating answers.

### Architecture

```mermaid
flowchart LR
    subgraph Ingestion["📥 Data Ingestion"]
        Schema["Schema Extraction"]
        Sample["Sample Data"]
        Chunk["Text Chunking"]
        Embed["Embedding Generation"]
    end

    subgraph Storage["💾 Vector Storage"]
        PGV[(pgvector)]
    end

    subgraph Retrieval["🔍 Retrieval"]
        Query["User Query"]
        QEmbed["Query Embedding"]
        Search["Similarity Search"]
    end

    subgraph Generation["✨ Generation"]
        Prompt["Prompt Construction"]
        LLM["LLM Call"]
        Response["Response"]
    end

    Schema --> Chunk
    Sample --> Chunk
    Chunk --> Embed
    Embed --> PGV
    Query --> QEmbed
    QEmbed --> Search
    PGV --> Search
    Search --> Prompt
    Prompt --> LLM
    LLM --> Response
```

### Components

#### 1. RAGService Class

Located in: [`backend/app/services/rag_service.py`](backend/app/services/rag_service.py)

**Key Methods:**

```python
class RAGService:
    def __init__(self):
        # Initialize OpenAI embeddings and LLM
        self.embeddings = OpenAIEmbeddings(...)
        self.llm = ChatOpenAI(...)
        self.text_splitter = RecursiveCharacterTextSplitter(...)

    def create_vector_store(self, connection_id, schema, sample_data):
        # Creates vector store from database schema
        
    def query_with_rag(self, user_query, connection_id):
        # Performs RAG-based query answering
        
    def generate_query(self, user_intent, schema, db_type):
        # Generates SQL/MongoDB query from natural language
```

#### 2. Embedding Generation

**Model:** OpenAI `text-embedding-ada-002`
- **Dimensions:** 1536
- **Context Window:** 8192 tokens
- **Cost:** ~$0.0001 per 1K tokens

**Process:**
1. Extract schema from connected database
2. Convert tables/columns to text descriptions
3. Sample data from each table (up to 10 rows)
4. Split text into chunks (1000 chars, 200 overlap)
5. Generate embeddings for each chunk
6. Store in pgvector with metadata

#### 3. Vector Search

**Similarity Metric:** Cosine similarity

**Search Parameters:**
- **Top K:** 3 most relevant chunks
- **Filter:** By connection_id (collection name)
- **Threshold:** Minimum similarity score (optional)

**Query Flow:**
```python
# 1. Embed user query
query_embedding = embeddings.embed_query(user_query)

# 2. Search vector store
results = vector_store.similarity_search(
    query=user_query,
    k=3,
    filter={"connection_id": connection_id}
)

# 3. Construct context
context = "\n".join([doc.page_content for doc in results])
```

#### 4. Prompt Engineering

**System Prompt Template:**
```
You are an AI assistant helping users query their database.
Use the following context about the database schema and data to answer the question.
If you need to suggest a query, provide it in the appropriate format.

Context: {context}

Question: {question}

Answer:
```

**Prompt Strategy:**
- Include schema context for table/column awareness
- Add sample data for value examples
- Specify output format (SQL vs MongoDB)
- Request step-by-step reasoning for complex queries

---

## Authentication Flow

### JWT-Based Authentication

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database

    U->>F: Enter credentials
    F->>B: POST /api/auth/login
    B->>DB: Fetch user by email
    DB->>B: Return user record
    B->>B: Verify password (bcrypt)
    B->>B: Generate JWT token
    B->>F: Return {access_token}
    F->>F: Store token in localStorage
    F->>U: Redirect to dashboard

    Note over U,F: Subsequent requests
    F->>B: API call with Authorization: Bearer <token>
    B->>B: Validate JWT signature
    B->>B: Extract user_id from payload
    B->>DB: Process request
    B->>F: Return data
```

### Token Structure

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user@example.com",
  "user_id": 123,
  "exp": 1705315200,
  "iat": 1704710400
}
```

**Security:**
- Algorithm: HS256 (HMAC + SHA-256)
- Expiration: 7 days
- Secret: 32+ character random string
- Storage: localStorage (frontend)

### Password Security

**Hashing:** bcrypt with salt rounds 12

```python
# Hashing
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password_bytes, salt)

# Verification
bcrypt.checkpw(plain_bytes, hashed_bytes)
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── Login (Public)
└── Dashboard (Protected)
    ├── Navigation
    ├── Stats Cards
    └── Feature Links
        ├── Connections
        │   ├── Connection List
        │   ├── Connection Form
        │   └── Delete Confirmation
        ├── ChatInterface
        │   ├── Message List
        │   ├── Input Form
        │   └── Connection Selector
        └── Settings
            ├── Provider Selector
            ├── Model Dropdown
            └── API Key Input
```

### State Management

**Local State (useState):**
- Form inputs
- UI toggles (show/hide)
- Loading states
- Error messages

**Global State (localStorage):**
- JWT token
- User preferences

**Server State (API):**
- Connection list
- Query history
- User settings

### API Client

Located in: [`frontend/src/api/client.js`](frontend/src/api/client.js)

```javascript
// Axios instance with interceptors
const client = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor adds auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API modules
export const auth = { register, login };
export const connections = { list, create, delete };
export const query = { execute, getHistory };
export const settings = { get, update, getProviders };
```

### Styling Strategy

**TailwindCSS Configuration:**

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#8B5CF6',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    }
  }
}
```

**Custom CSS Classes:**

```css
/* Glassmorphism cards */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Animated background */
.animated-bg {
  background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
}
```

---

## Development Guidelines

### Code Style

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Docstrings for all public methods

```python
def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db)
) -> ConnectionResponse:
    """
    Create a new database connection and index it for RAG.
    
    Args:
        connection: Connection creation parameters
        db: Database session
        
    Returns:
        Created connection details
        
    Raises:
        HTTPException: If connection validation fails
    """
    # Implementation
```

**JavaScript (Frontend):**
- Use ESLint with React rules
- Functional components with hooks
- PropTypes or TypeScript (future)
- Destructure props

```javascript
const ChatInterface = ({ connectionId }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Implementation
  };
  
  return (
    <div className="chat-container">
      {/* JSX */}
    </div>
  );
};
```

### Testing Strategy

**Backend Tests:**
```python
# tests/test_connections.py
def test_create_connection(client, auth_token):
    response = client.post(
        "/api/connections/",
        json={
            "name": "Test DB",
            "db_type": "postgresql",
            "connection_string": "postgresql://..."
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test DB"
```

**Frontend Tests:**
```javascript
// src/components/__tests__/Login.test.js
test('submits login form', async () => {
  render(<Login onLogin={mockLogin} />);
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  
  fireEvent.click(screen.getByText(/sign in/i));
  
  await waitFor(() => {
    expect(mockLogin).toHaveBeenCalled();
  });
});
```

### Git Workflow

1. **Branch Naming:**
   - Features: `feature/add-mysql-support`
   - Bugs: `bugfix/connection-timeout`
   - Docs: `docs/api-examples`

2. **Commit Messages:**
   ```
   feat: add MongoDB connector
   fix: resolve connection leak in PostgreSQL
   docs: update API reference
   test: add auth endpoint tests
   ```

3. **Pull Request Process:**
   - Create feature branch
   - Make changes with tests
   - Run full test suite
   - Submit PR with description
   - Code review required
   - Merge to main

---

## Deployment Architecture

### Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
```

### AWS Deployment

```mermaid
flowchart TB
    subgraph Users["🌐 Users"]
        Browser["Web Browser"]
    end

    subgraph AWS["☁️ AWS Cloud"]
        subgraph Network["Network Layer"]
            Route53["Route 53"]
            CloudFront["CloudFront CDN"]
            ALB["Application Load Balancer"]
        end

        subgraph Compute["Compute Layer"]
            ECS["ECS Fargate"]
            FrontendTask["Frontend Task"]
            BackendTask["Backend Task"]
        end

        subgraph Data["Data Layer"]
            RDS["RDS PostgreSQL"]
            S3["S3 Buckets"]
            Secrets["Secrets Manager"]
        end
    end

    Browser --> Route53
    Route53 --> CloudFront
    CloudFront --> ALB
    ALB --> ECS
    ECS --> FrontendTask
    ECS --> BackendTask
    BackendTask --> RDS
    BackendTask --> Secrets
    FrontendTask --> S3
```

### Environment-Specific Configurations

| Environment | Frontend URL | Backend URL | Database |
|-------------|--------------|-------------|----------|
| **Development** | localhost:3000 | localhost:8000 | Local Docker |
| **Staging** | staging.dataquery.ai | api-staging.dataquery.ai | RDS staging |
| **Production** | app.dataquery.ai | api.dataquery.ai | RDS production |

---

<div align="center">

**📚 Documentation Complete**

[⬅️ User Guide](USER_GUIDE.md) • [🚀 Deployment Guide →](DEPLOYMENT.md)

</div>
