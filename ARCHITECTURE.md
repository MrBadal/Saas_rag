# System Architecture

## Overview

The Universal RAG-Powered Database Query Platform is a multi-tier SaaS application that enables users to query their databases using natural language through AI-powered semantic search and retrieval augmented generation (RAG).

## High-Level Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Frontend (React)            │
│  - Chat Interface                   │
│  - Connection Management            │
│  - Authentication                   │
└──────────────┬──────────────────────┘
               │ REST API
               ▼
┌─────────────────────────────────────┐
│      Backend (FastAPI)              │
│  ┌─────────────────────────────┐   │
│  │   API Layer                 │   │
│  │  - Auth, Connections, Query │   │
│  └────────────┬────────────────┘   │
│               │                     │
│  ┌────────────▼────────────────┐   │
│  │   RAG Service               │   │
│  │  - Embeddings (OpenAI)      │   │
│  │  - Vector Search            │   │
│  │  - LLM Integration          │   │
│  └────────────┬────────────────┘   │
│               │                     │
│  ┌────────────▼────────────────┐   │
│  │   Database Connectors       │   │
│  │  - PostgreSQL               │   │
│  │  - MongoDB                  │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│  PostgreSQL │  │ User         │
│  (pgvector) │  │ Databases    │
│             │  │ (PG/Mongo)   │
│  - Users    │  └──────────────┘
│  - Conns    │
│  - Vectors  │
│  - History  │
└─────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology:** React 18 + TailwindCSS

**Components:**
- `Login.js` - Authentication UI
- `Dashboard.js` - Main landing page
- `Connections.js` - Database connection management
- `ChatInterface.js` - Natural language query interface

**Features:**
- JWT-based authentication
- Real-time chat interface
- Connection management UI
- Query history display

### 2. Backend API Layer

**Technology:** FastAPI (Python)

**Modules:**
- `app/api/auth.py` - User authentication & JWT tokens
- `app/api/connections.py` - Database connection CRUD
- `app/api/query.py` - Query execution & RAG

**Responsibilities:**
- Request validation
- Authentication & authorization
- Business logic orchestration
- Response formatting

### 3. RAG Service Layer

**Technology:** LangChain + OpenAI

**Core Functions:**

**a) Embedding Generation**
- Converts database schema and sample data to text
- Generates vector embeddings using OpenAI
- Stores in pgvector for semantic search

**b) Vector Store**
- Uses pgvector extension in PostgreSQL
- Stores embeddings with metadata
- Enables similarity search

**c) Retrieval**
- Semantic search for relevant context
- Retrieves top-k similar documents
- Provides context to LLM

**d) Generation**
- Constructs prompts with retrieved context
- Calls OpenAI LLM
- Generates natural language responses

**e) Query Planning**
- Converts user intent to SQL/MongoDB queries
- Schema-aware query generation
- Validation and optimization

### 4. Database Connector Layer

**PostgreSQL Connector:**
- SQLAlchemy-based connection
- Schema introspection
- Query execution
- Connection pooling

**MongoDB Connector:**
- PyMongo client
- Collection discovery
- Document sampling
- Query execution

**Features:**
- Connection validation
- Error handling
- Secure credential storage
- Connection pooling

### 5. Data Layer

**Application Database (PostgreSQL with pgvector):**

**Tables:**
- `users` - User accounts
- `database_connections` - User database connections
- `query_history` - Query logs
- `langchain_pg_collection` - Vector embeddings (LangChain)
- `langchain_pg_embedding` - Vector data (LangChain)

**User Databases:**
- PostgreSQL instances
- MongoDB instances
- Connected via secure connection strings

## Data Flow

### Connection Creation Flow

```
1. User submits connection details
   ↓
2. Backend validates credentials
   ↓
3. Connector establishes test connection
   ↓
4. Schema extraction & sampling
   ↓
5. Text conversion & chunking
   ↓
6. Embedding generation (OpenAI)
   ↓
7. Vector storage (pgvector)
   ↓
8. Connection saved to database
```

### Query Execution Flow

```
1. User submits natural language query
   ↓
2. Backend retrieves connection details
   ↓
3. RAG Service performs semantic search
   ↓
4. Relevant context retrieved from vectors
   ↓
5. Prompt construction with context
   ↓
6. LLM generates response
   ↓
7. Optional: Generate & execute DB query
   ↓
8. Response returned to user
   ↓
9. Query saved to history
```

## Security Architecture

### Authentication
- JWT tokens with 7-day expiration
- Bcrypt password hashing
- Token-based API access

### Data Protection
- Connection strings stored encrypted (TODO)
- HTTPS/TLS for all communications
- Environment-based secrets management

### Multi-Tenancy
- User-level data isolation
- Connection ownership validation
- Query history segregation

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer distribution
- Database connection pooling

### Vertical Scaling
- Async request handling (FastAPI)
- Efficient vector operations
- Query result caching

### Performance Optimization
- Vector index optimization
- Connection pooling
- Response caching
- Batch processing for embeddings

## Technology Stack

### Backend
- **Framework:** FastAPI 0.109
- **ORM:** SQLAlchemy 2.0
- **Database Drivers:** psycopg2, pymongo
- **AI/ML:** LangChain, OpenAI
- **Vector Store:** pgvector
- **Auth:** python-jose, passlib

### Frontend
- **Framework:** React 18
- **Styling:** TailwindCSS
- **HTTP Client:** Axios
- **Routing:** React Router v6

### Infrastructure
- **Database:** PostgreSQL 16 with pgvector
- **Containerization:** Docker
- **Orchestration:** Docker Compose / ECS
- **Cloud:** AWS (RDS, ECS, S3, ALB)

## Extension Points

### Adding New Database Connectors
1. Create connector class in `services/connectors.py`
2. Implement `connect()`, `get_schema()`, `execute_query()`
3. Register in `get_connector()` factory
4. Update frontend dropdown

### Custom LLM Integration
1. Modify `services/rag_service.py`
2. Replace OpenAI client with custom LLM
3. Adjust prompt templates
4. Update configuration

### Advanced RAG Features
- Multi-query retrieval
- Hybrid search (keyword + semantic)
- Re-ranking algorithms
- Query result caching
- Streaming responses

## Monitoring & Observability

### Metrics
- API latency
- Database query performance
- Vector search time
- LLM API calls & costs
- Error rates

### Logging
- Structured JSON logs
- Request/response logging
- Error tracking
- Audit trails

### Alerting
- API downtime
- Database connection failures
- High error rates
- Cost thresholds

## Future Enhancements

### Phase 2 Features
- Additional database connectors (MySQL, Redis, etc.)
- File ingestion (CSV, JSON, PDF)
- Advanced visualization
- Query result export
- Collaborative features
- API rate limiting
- Usage analytics dashboard
- Custom embedding models
- Fine-tuned LLMs for specific domains
