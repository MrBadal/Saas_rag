# ⚡ Quick Start Guide - Self-Hosted RAG

## 🎯 Goal
Get your **free, self-hosted RAG system** running in **under 10 minutes**.

---

## ✅ Prerequisites Checklist

- [ ] Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- [ ] Docker Compose installed (included with Docker Desktop)
- [ ] 4GB RAM available
- [ ] 20GB disk space free
- [ ] Internet connection (for initial setup)

---

## 🚀 3-Step Setup

### Step 1: Get the Code
```bash
# If you have git
git clone <your-repo-url>
cd <repo-name>

# Or download and extract ZIP
```

### Step 2: Configure
```bash
# Copy environment template
cp .env.example .env

# Edit if needed (optional - defaults work fine)
# nano .env
```

### Step 3: Run Setup Script

**Windows:**
```cmd
setup-local.bat
```

**Linux/Mac:**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

**That's it!** ☕ Grab coffee while it sets up (~5-10 minutes)

---

## 🌐 Access Your Application

Once setup completes, open your browser:

### Main Application
```
http://localhost:3000
```

### API Documentation
```
http://localhost:8000/docs
```

### Health Checks
```bash
# Check all services
curl http://localhost:8001/health  # Embeddings ✓
curl http://localhost:11434/api/tags  # Ollama ✓
curl http://localhost:8000/docs  # Backend ✓
```

---

## 📝 First Steps

### 1. Create Account
- Open http://localhost:3000
- Click "Sign Up"
- Enter email and password
- Click "Create Account"

### 2. Add Your First Database

**Example: PostgreSQL**
```
Name: My Test DB
Type: PostgreSQL
Connection String: postgresql://user:password@host:5432/database
```

**Example: MongoDB**
```
Name: My Mongo DB
Type: MongoDB
Connection String: mongodb://user:password@host:27017/database
```

Click "Connect" - system will automatically index your database!

### 3. Ask Your First Question

Select your connection and try:
```
"Show me the database schema"
"How many tables/collections are there?"
"What data do you have?"
```

---

## 🎯 Example Queries

### General
```
"What tables/collections exist?"
"Show me the schema"
"What's in the users table?"
```

### Data Exploration
```
"How many records in the orders table?"
"Show me sample data from products"
"What are the column names in customers?"
```

### Query Generation
```
"Generate a query to find all active users"
"Show me SQL for orders from last month"
"Create a query for revenue by product"
```

### Analysis
```
"What's the total count of users?"
"Find the most recent orders"
"Show me customers in California"
```

---

## 🔧 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ollama
docker-compose logs -f embedding-service
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Everything
```bash
docker-compose down
```

### Start Again
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

---

## 🐛 Troubleshooting

### Problem: Services won't start

**Solution:**
```bash
# Check Docker is running
docker ps

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problem: "Out of memory" errors

**Solution 1: Use smaller model**
```bash
docker exec ollama ollama pull tinyllama
# Edit .env: OLLAMA_MODEL=tinyllama
docker-compose restart backend
```

**Solution 2: Add swap space (Linux)**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problem: Slow responses

**Solutions:**
1. Use `tinyllama` model (see above)
2. Close other applications
3. Allocate more RAM to Docker
4. Use a more powerful machine

### Problem: Can't connect to database

**Check:**
- Connection string format is correct
- Database is accessible from Docker network
- Use `host.docker.internal` instead of `localhost` for local databases
- Firewall allows connections

**Example fix for local PostgreSQL:**
```
# Instead of:
postgresql://user:pass@localhost:5432/db

# Use:
postgresql://user:pass@host.docker.internal:5432/db
```

### Problem: Embedding service fails

**Solution:**
```bash
docker-compose logs embedding-service
docker-compose restart embedding-service

# If still failing, rebuild
docker-compose build embedding-service
docker-compose up -d embedding-service
```

---

## 📊 What's Running?

After successful setup, you have:

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | React web interface |
| **Backend** | 8000 | FastAPI REST API |
| **Embeddings** | 8001 | Local embedding generation |
| **Ollama** | 11434 | Local LLM |
| **PostgreSQL** | 5432 | Application database |

---

## 🎓 Next Steps

### Learn More
- Read [README_LOCAL.md](README_LOCAL.md) for detailed features
- Check [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for architecture
- Review [COMPARISON.md](COMPARISON.md) for cloud vs self-hosted

### Deploy to Production
- Follow [AWS_DEPLOYMENT_LOCAL.md](AWS_DEPLOYMENT_LOCAL.md)
- Set up HTTPS
- Configure backups
- Enable monitoring

### Customize
- Try different Ollama models
- Adjust embedding parameters
- Modify prompts for better results
- Add custom database connectors

---

## 💡 Pro Tips

### 1. Model Selection
```bash
# List available models
docker exec ollama ollama list

# Pull new model
docker exec ollama ollama pull mistral

# Update .env
OLLAMA_MODEL=mistral

# Restart
docker-compose restart backend
```

### 2. Performance Tuning
```env
# In .env - adjust based on your hardware
OLLAMA_NUM_PARALLEL=2  # Concurrent requests
OLLAMA_NUM_GPU=0  # GPU layers (0 for CPU)
```

### 3. Database Connection Tips
- Test connection string separately first
- Use read-only credentials when possible
- Start with small databases for testing
- Monitor resource usage

### 4. Monitoring
```bash
# Watch resource usage
docker stats

# Check disk space
df -h

# Monitor logs in real-time
docker-compose logs -f | grep ERROR
```

---

## 🎉 Success Checklist

After setup, verify:

- [ ] All containers running (`docker-compose ps`)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Backend API works (http://localhost:8000/docs)
- [ ] Embedding service healthy (http://localhost:8001/health)
- [ ] Ollama has model (`docker exec ollama ollama list`)
- [ ] Can create account
- [ ] Can add database connection
- [ ] Can query database
- [ ] Responses make sense

---

## 📞 Getting Help

### Check Logs First
```bash
docker-compose logs -f
```

### Common Log Locations
- Backend errors: `docker-compose logs backend`
- Ollama issues: `docker-compose logs ollama`
- Embedding problems: `docker-compose logs embedding-service`
- Database issues: `docker-compose logs postgres`

### Still Stuck?
1. Check [Troubleshooting](#-troubleshooting) section above
2. Review [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
3. Check Docker/Ollama documentation
4. Open GitHub issue with logs

---

## 🚀 You're Ready!

Your self-hosted RAG system is now running! 

**Key Benefits:**
- ✅ $0 API costs
- ✅ Complete privacy
- ✅ Full control
- ✅ Unlimited queries

**Start querying your databases with AI!** 🎯

---

## 📚 Quick Reference

### Essential Commands
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Rebuild
docker-compose build
```

### Essential URLs
```
Frontend:    http://localhost:3000
Backend:     http://localhost:8000
API Docs:    http://localhost:8000/docs
Embeddings:  http://localhost:8001
Ollama:      http://localhost:11434
```

### Essential Files
```
.env                    - Configuration
docker-compose.yml      - Service definitions
README_LOCAL.md         - Full documentation
IMPLEMENTATION_PLAN.md  - Technical details
AWS_DEPLOYMENT_LOCAL.md - Production deployment
```

---

**Happy querying!** 🎉
