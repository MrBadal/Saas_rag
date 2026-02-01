# 🚀 Universal RAG-Powered Database Query Platform

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**🤖 AI-Powered Natural Language Database Queries with RAG**

[📖 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [🎥 Demo](#demo) • [🛠️ Tech Stack](#tech-stack)

</div>

---

## ✨ What is DataQuery AI?

**DataQuery AI** is a powerful SaaS platform that revolutionizes how you interact with databases. Instead of writing complex SQL or MongoDB queries, simply ask questions in plain English! Our advanced RAG (Retrieval-Augmented Generation) system understands your database schema and provides intelligent, context-aware answers.

### 🎯 Key Features

| Feature | Description | Emoji |
|---------|-------------|-------|
| **🔌 Universal Connectors** | Connect to PostgreSQL and MongoDB databases seamlessly | 🔌 |
| **🧠 RAG-Powered Search** | Semantic search across your database schema and data | 🧠 |
| **💬 Natural Language Queries** | Ask questions in plain English, get instant answers | 💬 |
| **🤖 Multi-LLM Support** | Choose from OpenAI, OpenRouter, Gemini, and more | 🤖 |
| **🔐 Secure Authentication** | JWT-based auth with bcrypt password hashing | 🔐 |
| **📊 Query History** | Track and review all your past queries | 📊 |
| **⚡ Real-time Responses** | Fast, streaming AI-powered responses | ⚡ |
| **🎨 Modern UI** | Beautiful, responsive interface with TailwindCSS | 🎨 |
| **🐳 Docker Ready** | One-command deployment with Docker Compose | 🐳 |
| **☁️ AWS-Ready** | Production-ready AWS deployment configuration | ☁️ |

---

## 🚀 Quick Start

Get up and running in under 5 minutes!

### Prerequisites

- 🐳 [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- 🔑 [OpenAI API Key](https://platform.openai.com/account/api-keys) (or other LLM provider)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/rag-saas-platform.git
cd rag-saas-platform

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start all services
docker-compose up -d

# 4. Initialize the database
docker-compose exec backend python -c "from app.models.database import init_db; init_db()"
```

🎉 **That's it!** Access your application at:
- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

### Option 2: Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

</details>

---

## 📸 Screenshots

<div align="center">

### 🎨 Beautiful Login Page
*Modern glassmorphism design with animated backgrounds*

### 📊 Intuitive Dashboard  
*Quick access to connections, chat, and analytics*

### 💬 AI Chat Interface
*Natural language queries with syntax-highlighted results*

### 🔌 Connection Management
*Easy database connection setup with validation*

### ⚙️ Flexible Settings
*Multi-LLM provider configuration*

</div>

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| 🚀 **FastAPI** | High-performance Python web framework | 0.115.0 |
| 🗄️ **SQLAlchemy** | ORM for database operations | 2.0.36 |
| 🔍 **LangChain** | LLM orchestration and RAG | 0.3.0 |
| 🧠 **OpenAI** | Embeddings and chat completions | 1.0.0+ |
| 📦 **pgvector** | Vector similarity search in PostgreSQL | 0.2.5 |
| 🔐 **JWT** | Authentication tokens | python-jose |

### Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| ⚛️ **React** | UI library | 18.2.0 |
| 🎨 **TailwindCSS** | Utility-first CSS framework | 3.4.1 |
| 🔄 **Axios** | HTTP client | 1.6.5 |
| 🛣️ **React Router** | Client-side routing | 6.21.3 |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| 🐳 **Docker** | Containerization |
| 🐘 **PostgreSQL** | Primary database with pgvector extension |
| 🍃 **MongoDB** | Supported data source |
| ☁️ **AWS** | Cloud deployment (ECS, RDS, ALB) |

---

## 📚 Documentation

| Document | Description | Link |
|----------|-------------|------|
| 📖 **User Guide** | End-user documentation for using the platform | [USER_GUIDE.md](USER_GUIDE.md) |
| 🛠️ **Getting Started** | Developer onboarding and local setup | [GETTING_STARTED.md](GETTING_STARTED.md) |
| ⚙️ **Technical Docs** | Architecture, API reference, and code organization | [TECHNICAL.md](TECHNICAL.md) |
| 🚀 **Deployment** | Production deployment guides | [DEPLOYMENT.md](DEPLOYMENT.md) |
| 🔌 **API Reference** | Complete API endpoint documentation | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |

---

## 🎯 Use Cases

### 💼 For Business Analysts
- Query sales data without knowing SQL
- Get instant insights from customer databases
- Generate reports with natural language

### 👨‍💻 For Developers
- Quickly explore unfamiliar databases
- Generate query templates
- Debug data issues faster

### 📊 For Data Scientists
- Explore datasets conversationally
- Get schema overviews instantly
- Validate data assumptions

### 🏢 For Teams
- Share database knowledge through AI
- Onboard new team members faster
- Maintain query history and context

---

## 🔌 Supported Databases

| Database | Status | Connection String Example |
|----------|--------|---------------------------|
| 🐘 **PostgreSQL** | ✅ Fully Supported | `postgresql://user:pass@host:5432/dbname` |
| 🍃 **MongoDB** | ✅ Fully Supported | `mongodb+srv://user:pass@cluster.mongodb.net/dbname` |
| 🔮 **MySQL** | 🚧 Coming Soon | - |
| 🎯 **Redis** | 🚧 Coming Soon | - |
| 📊 **BigQuery** | 🚧 Coming Soon | - |

---

## 🤖 Supported LLM Providers

| Provider | Models | Status |
|----------|--------|--------|
| 🧠 **OpenAI** | GPT-4, GPT-3.5-turbo | ✅ Supported |
| 🌐 **OpenRouter** | 100+ models | ✅ Supported |
| 💎 **Google Gemini** | Gemini Pro | ✅ Supported |
| 🎭 **Anthropic** | Claude 3 Opus/Sonnet | ✅ Supported |
| 🦙 **Ollama** | Local models | ✅ Supported |

---

## 🎥 Demo

### Example Queries

```
💬 "Show me all users who signed up last month"
💬 "What's the average order value by category?"
💬 "Find customers who haven't made a purchase in 90 days"
💬 "List the top 10 products by revenue"
```

### Sample Response

```markdown
**Answer:**
The top 10 products by revenue are:

1. Wireless Headphones - $45,230
2. Smart Watch - $38,900
3. Laptop Stand - $22,450
...

**Generated Query:**
```sql
SELECT product_name, SUM(price * quantity) as revenue
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10;
```

**Results:** 10 rows returned
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to branch (`git push origin feature/amazing-feature`)
5. 🔃 Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🦜 [LangChain](https://langchain.com/) for the amazing RAG framework
- ⚡ [FastAPI](https://fastapi.tiangolo.com/) for the blazing-fast backend
- 🎨 [TailwindCSS](https://tailwindcss.com/) for the beautiful styling
- 🧠 [OpenAI](https://openai.com/) for the powerful LLM capabilities

---

## 📞 Support

| Channel | Link |
|---------|------|
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/yourusername/rag-saas-platform/issues) |
| 💡 **Feature Requests** | [GitHub Discussions](https://github.com/yourusername/rag-saas-platform/discussions) |
| 📧 **Email** | support@dataqueryai.com |
| 💬 **Discord** | [Join our community](https://discord.gg/dataqueryai) |

---

<div align="center">

**⭐ Star us on GitHub if you find this project helpful!**

Made with ❤️ and 🤖 by the DataQuery AI Team

</div>
