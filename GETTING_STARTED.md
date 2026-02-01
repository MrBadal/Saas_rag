# 🚀 Getting Started Guide

Welcome to **DataQuery AI**! This guide will help you set up the development environment and get the platform running locally.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker-recommended)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

| Software | Version | Download Link | Verification |
|----------|---------|---------------|--------------|
| 🐳 **Docker** | 20.10+ | [Get Docker](https://docs.docker.com/get-docker/) | `docker --version` |
| 🐳 **Docker Compose** | 2.0+ | Included with Docker | `docker-compose --version` |
| 🐍 **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) | `python --version` |
| 📦 **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) | `node --version` |
| 📦 **npm** | 9+ | Included with Node.js | `npm --version` |
| 🔑 **Git** | 2.30+ | [git-scm.com](https://git-scm.com/) | `git --version` |

### API Keys Required

You'll need at least one of the following API keys:

| Provider | Purpose | Get Key |
|----------|---------|---------|
| 🧠 **OpenAI** | Embeddings & Chat | [platform.openai.com](https://platform.openai.com/account/api-keys) |
| 🌐 **OpenRouter** | Access to 100+ models | [openrouter.ai](https://openrouter.ai/keys) |
| 💎 **Google Gemini** | Alternative LLM | [makersuite.google.com](https://makersuite.google.com/app/apikey) |

> 💡 **Tip:** OpenAI is recommended for beginners as it provides the most reliable embeddings.

---

## Quick Start with Docker (Recommended)

The fastest way to get started is using Docker Compose. This sets up the entire stack with one command.

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-saas-platform.git

# Navigate to project directory
cd rag-saas-platform
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

**Minimum required configuration:**

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Change if you have port conflicts
# DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb
# SECRET_KEY=your-secret-key-for-jwt
```

### Step 3: Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps
```

### Step 4: Initialize the Database

```bash
# Create database tables
docker-compose exec backend python -c "from app.models.database import init_db; init_db()"

# Verify initialization
# You should see no errors
```

### Step 5: Access the Application

🎉 **Success!** Your application is now running:

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 **Frontend** | http://localhost:3000 | React web application |
| 🔌 **Backend API** | http://localhost:8000 | FastAPI server |
| 📚 **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| 📊 **ReDoc** | http://localhost:8000/redoc | Alternative API docs |

### Step 6: Create Your First User

1. Navigate to http://localhost:3000
2. Click "Create Account"
3. Enter your email and password
4. Start exploring!

---

## Manual Setup

If you prefer not to use Docker, follow these manual setup instructions.

### Backend Setup

#### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

#### 3. Set Up PostgreSQL with pgvector

**Option A: Using Docker (for PostgreSQL only)**

```bash
# Run PostgreSQL with pgvector
docker run -d \
  --name rag-postgres \
  -e POSTGRES_USER=raguser \
  -e POSTGRES_PASSWORD=ragpass \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

**Option B: Local PostgreSQL Installation**

```bash
# macOS with Homebrew
brew install postgresql
brew install pgvector

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
# Then install pgvector extension manually

# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start   # Linux
```

#### 4. Configure Environment

```bash
# Create .env file in project root
cat > ../.env << EOF
OPENAI_API_KEY=sk-your-api-key-here
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
EOF
```

#### 5. Initialize Database

```bash
# Run from backend directory with venv activated
python -c "from app.models.database import init_db; init_db()"
```

#### 6. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
# From project root
cd frontend
```

#### 2. Install Dependencies

```bash
# Install npm packages
npm install

# Verify installation
npm list react
```

#### 3. Configure API URL

Create a `.env` file in the frontend directory:

```bash
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
```

#### 4. Start Development Server

```bash
# Start React development server
npm start
```

The browser should automatically open at http://localhost:3000

---

## Environment Configuration

### Complete Environment Variables Reference

```env
# ============================================
# 🔑 API Keys (Required)
# ============================================

# OpenAI (Recommended for embeddings)
OPENAI_API_KEY=sk-your-openai-key-here

# OpenRouter (Alternative, supports 100+ models)
OPENROUTER_API_KEY=sk-or-your-openrouter-key

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# ============================================
# 🗄️ Database Configuration
# ============================================

# PostgreSQL with pgvector
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb

# ============================================
# 🔐 Application Security
# ============================================

# Secret key for JWT token generation
SECRET_KEY=your-super-secret-key-min-32-chars-long

# Environment: development, staging, production
ENVIRONMENT=development

# ============================================
# 🤖 Ollama Configuration (Optional)
# ============================================

# Local LLM server URL
OLLAMA_HOST=http://localhost:11434

# ============================================
# ☁️ AWS Configuration (Optional, for deployment)
# ============================================

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

---

## Development Workflow

### Project Structure

```
rag-saas-platform/
├── 📁 backend/                 # FastAPI backend
│   ├── 📁 app/
│   │   ├── 📁 api/            # API routes
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── connections.py # Database connections
│   │   │   ├── query.py       # Query execution
│   │   │   └── settings.py    # User settings
│   │   ├── 📁 core/           # Core configuration
│   │   │   └── config.py      # Settings management
│   │   ├── 📁 models/         # Database models
│   │   │   └── database.py    # SQLAlchemy models
│   │   ├── 📁 services/       # Business logic
│   │   │   ├── connectors.py  # Database connectors
│   │   │   └── rag_service.py # RAG implementation
│   │   └── main.py            # Application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── 📁 frontend/               # React frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # React components
│   │   │   ├── Login.js
│   │   │   ├── Dashboard.js
│   │   │   ├── ChatInterface.js
│   │   │   ├── Connections.js
│   │   │   └── Settings.js
│   │   ├── 📁 api/            # API client
│   │   │   └── client.js
│   │   ├── App.js
│   │   └── index.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

### Common Development Tasks

#### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

#### Restart Services

```bash
# Restart specific service
docker-compose restart backend

# Restart all
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

#### Run Backend Tests

```bash
# With Docker
docker-compose exec backend pytest

# Manual setup
cd backend
pytest
```

#### Database Migrations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U raguser -d ragdb

# List tables
\dt

# View connection data
SELECT * FROM database_connections;

# View query history
SELECT * FROM query_history ORDER BY created_at DESC;
```

#### Frontend Development

```bash
# Run linter
cd frontend
npm run lint

# Build for production
npm run build

# Run tests
npm test
```

---

## Troubleshooting

### Common Issues and Solutions

#### 🔴 Issue: "Cannot connect to database"

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. Check if PostgreSQL container is running:
```bash
docker-compose ps
```

2. Verify database URL in `.env`:
```env
# For Docker Compose:
DATABASE_URL=postgresql://raguser:ragpass@postgres:5432/ragdb

# For local PostgreSQL:
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb
```

3. Restart PostgreSQL:
```bash
docker-compose restart postgres
docker-compose exec backend python -c "from app.models.database import init_db; init_db()"
```

---

#### 🔴 Issue: "OpenAI API key invalid"

**Symptoms:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solutions:**

1. Verify your API key at [OpenAI Platform](https://platform.openai.com/account/api-keys)

2. Check `.env` file is loaded:
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY  # macOS/Linux
set OPENAI_API_KEY    # Windows
```

3. Restart services after updating `.env`:
```bash
docker-compose down
docker-compose up -d
```

---

#### 🔴 Issue: "Port already in use"

**Symptoms:**
```
Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solutions:**

1. Find and stop the process using the port:
```bash
# macOS/Linux
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
lsof -ti:5432 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

2. Or use different ports in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Frontend on port 3001
  - "8001:8000"  # Backend on port 8001
```

---

#### 🔴 Issue: "CORS errors in browser"

**Symptoms:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solutions:**

1. Verify backend CORS settings in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Check `REACT_APP_API_URL` in frontend `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

---

#### 🔴 Issue: "Module not found" errors

**Solutions:**

1. Reinstall dependencies:
```bash
# Backend
rm -rf backend/venv
python -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
rm -rf frontend/node_modules
npm install --prefix frontend
```

2. Clear Docker cache:
```bash
docker-compose down -v
docker system prune -a
```

---

### Getting Help

If you encounter issues not covered here:

1. 📖 Check [TECHNICAL.md](TECHNICAL.md) for detailed technical documentation
2. 🐛 Search [existing issues](https://github.com/yourusername/rag-saas-platform/issues)
3. 💬 Join our [Discord community](https://discord.gg/dataqueryai)
4. 📧 Email support: support@dataqueryai.com

---

## Next Steps

Now that you have the platform running:

### 🎯 For Users

1. 📖 Read the [User Guide](USER_GUIDE.md) to learn how to:
   - Connect your first database
   - Ask natural language questions
   - Configure LLM settings

### 👨‍💻 For Developers

1. ⚙️ Read [TECHNICAL.md](TECHNICAL.md) to understand:
   - System architecture
   - API reference
   - Code organization

2. 🚀 Read [DEPLOYMENT.md](DEPLOYMENT.md) to learn:
   - Production deployment
   - AWS configuration
   - Scaling strategies

### 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

---

<div align="center">

**🎉 You're all set! Happy querying!**

[⬅️ Back to README](README.md) • [📖 User Guide →](USER_GUIDE.md)

</div>
