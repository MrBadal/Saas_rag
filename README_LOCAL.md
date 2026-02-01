# 🚀 Self-Hosted RAG Database Query Platform

A **completely free, self-hosted** RAG-powered platform that lets users query their databases using natural language - **no external API costs**.

## ✨ Features

- 🆓 **100% Free** - No OpenAI or external API costs
- 🔒 **Privacy First** - All data stays on your infrastructure
- 🎯 **Plug & Play** - Users just provide database connection strings
- 🤖 **Smart AI** - Local embeddings + Ollama LLM
- 💾 **Multi-Database** - PostgreSQL, MongoDB support
- ⚡ **Fast Setup** - One command to start everything

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Your AWS Free Tier Instance         │
│                                             │
│  Frontend (React) ←→ Backend (FastAPI)     │
│                          ↓                  │
│  ┌──────────────────────┴────────────────┐ │
│  │  Local Embedding Service               │ │
│  │  (sentence-transformers)               │ │
│  └────────────────────────────────────────┘ │
│                          ↓                  │
│  ┌──────────────────────┴────────────────┐ │
│  │  Ollama (Local LLM)                    │ │
│  │  Models: llama3.2, phi3, tinyllama     │ │
│  └────────────────────────────────────────┘ │
│                          ↓                  │
│  ┌──────────────────────┴────────────────┐ │
│  │  PostgreSQL + pgvector                 │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

### Windows
```cmd
setup-local.bat
```

### Linux/Mac
```bash
chmod +x setup-local.sh
./setup-local.sh
```

That's it! 🎉

---

## 🌐 Access

After setup completes:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Embedding Service**: http://localhost:8001
- **Ollama**: http://localhost:11434

---

## 📖 How to Use

### 1. Create Account
- Open http://localhost:3000
- Sign up with email/password

### 2. Add Database Connection
- Click "Add Connection"
- Provide:
  - **Name**: My Database
  - **Type**: PostgreSQL or MongoDB
  - **Connection String**: `postgresql://user:pass@host:port/db`
- Click "Connect"
- System automatically indexes your database

### 3. Query Your Database
- Select your connection
- Ask questions in natural language:
  - "Show me all users"
  - "What's the total revenue?"
  - "Find orders from last month"
- Get instant answers!

---

## 🎯 Example Queries

### PostgreSQL
```
"Show me the schema of the users table"
"How many orders were placed yesterday?"
"What's the average order value by customer?"
"Generate a query to find inactive users"
```

### MongoDB
```
"Show me all collections"
"How many documents in the users collection?"
"Find users in California"
"What fields are in the products collection?"
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Local Models (Default)
USE_LOCAL_MODELS=true
EMBEDDING_SERVICE_URL=http://localhost:8001
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Database
DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb

# Security
SECRET_KEY=your-secret-key-here
```

### Model Options

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 2GB | Medium | Excellent | Production |
| **phi3** | 3.8GB | Medium | Very Good | Balanced |
| **tinyllama** | 637MB | Fast | Good | Low resources |

Change model:
```bash
docker exec ollama ollama pull tinyllama
# Update .env: OLLAMA_MODEL=tinyllama
docker-compose restart backend
```

---

## 🔧 Management

### View Logs
```bash
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Stop Everything
```bash
docker-compose down
```

### Update Application
```bash
git pull
docker-compose build
docker-compose up -d
```

---

## 🌍 Deploy to AWS Free Tier

See **[AWS_DEPLOYMENT_LOCAL.md](AWS_DEPLOYMENT_LOCAL.md)** for complete deployment guide.

**Quick Summary:**
1. Launch t2.micro EC2 instance (Ubuntu)
2. Install Docker & Docker Compose
3. Clone this repo
4. Run setup script
5. Access via public IP

**Cost**: $0/month (first year with AWS Free Tier)

---

## 📊 Performance

### Local Development (8GB RAM)
- Embedding: ~100ms for 10 texts
- LLM Response: 1-3 seconds
- Total Query: 2-5 seconds

### AWS t2.micro (1GB RAM)
- Embedding: ~200ms for 10 texts
- LLM Response: 3-8 seconds
- Total Query: 5-15 seconds

**Tip**: Use `tinyllama` model on t2.micro for better performance.

---

## 🔒 Security

### Development
- Default passwords in `.env.example`
- No HTTPS (localhost only)

### Production
- ✅ Change all default passwords
- ✅ Enable HTTPS (Let's Encrypt)
- ✅ Configure firewall
- ✅ Restrict SSH access
- ✅ Use strong SECRET_KEY

See [AWS_DEPLOYMENT_LOCAL.md](AWS_DEPLOYMENT_LOCAL.md) for security setup.

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Rebuild
docker-compose build
docker-compose up -d
```

### Out of memory
```bash
# Use smaller model
docker exec ollama ollama pull tinyllama

# Add swap (Linux)
sudo fallocate -l 2G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow responses
- Use `tinyllama` model
- Reduce vector search results (edit code: `k=3` → `k=1`)
- Add more RAM

### Can't connect to database
- Check connection string format
- Verify database is accessible from Docker network
- Check firewall rules

---

## 📚 Documentation

- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Complete implementation guide
- **[AWS_DEPLOYMENT_LOCAL.md](AWS_DEPLOYMENT_LOCAL.md)** - AWS deployment guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

---

## 🎯 Roadmap

### ✅ Completed
- Self-hosted embeddings
- Local LLM (Ollama)
- PostgreSQL & MongoDB support
- Docker deployment
- AWS Free Tier guide

### 🚧 In Progress
- Response caching
- Query optimization
- Better error handling

### 📋 Planned
- MySQL support
- Redis support
- File upload (CSV, JSON)
- Query history search
- Multi-user collaboration
- API rate limiting

---

## 💰 Cost Comparison

### Traditional (OpenAI)
- Embeddings: $0.0001/1K tokens
- LLM: $0.002/1K tokens
- **Monthly**: $50-500+ depending on usage

### Self-Hosted (This Solution)
- Embeddings: $0
- LLM: $0
- **Monthly**: $0 (AWS Free Tier) or ~$12 after

**Savings**: 100% of API costs! 💰

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **sentence-transformers** - Embedding models
- **pgvector** - Vector similarity search
- **LangChain** - RAG framework
- **FastAPI** - Backend framework
- **React** - Frontend framework

---

## 📞 Support

### Issues
- Check [Troubleshooting](#-troubleshooting) section
- Review logs: `docker-compose logs -f`
- Check service health: `docker-compose ps`

### Questions
- Open GitHub issue
- Check documentation files
- Review example queries

---

## 🎉 Success!

You now have a **completely self-hosted RAG system** that:
- ✅ Costs $0 in API fees
- ✅ Keeps all data private
- ✅ Works offline
- ✅ Scales with your needs

**Start querying your databases with AI - for free!** 🚀

---

Made with ❤️ for the open-source community
