# 🎯 Commands Cheatsheet

Quick reference for all commands you'll need to manage your self-hosted RAG system.

---

## 🚀 Initial Setup

### Windows
```cmd
setup-local.bat
```

### Linux/Mac
```bash
chmod +x setup-local.sh
./setup-local.sh
```

---

## 🐳 Docker Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend
docker-compose up -d ollama
docker-compose up -d embedding-service

# Start with logs visible
docker-compose up
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop but keep volumes
docker-compose stop

# Stop specific service
docker-compose stop backend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart ollama
```

### View Status
```bash
# List running containers
docker-compose ps

# Detailed status
docker ps

# Resource usage
docker stats
```

### View Logs
```bash
# All services (follow mode)
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ollama
docker-compose logs -f embedding-service
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100

# Since specific time
docker-compose logs --since 2024-01-01T00:00:00
```

### Build/Rebuild
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build embedding-service

# Build without cache
docker-compose build --no-cache

# Build and start
docker-compose up -d --build
```

### Clean Up
```bash
# Remove stopped containers
docker-compose rm

# Remove all (including volumes)
docker-compose down -v

# Remove unused images
docker image prune

# Remove everything
docker system prune -a
```

---

## 🤖 Ollama Commands

### Model Management
```bash
# List installed models
docker exec ollama ollama list

# Pull/download a model
docker exec ollama ollama pull llama3.2
docker exec ollama ollama pull phi3
docker exec ollama ollama pull tinyllama
docker exec ollama ollama pull mistral

# Remove a model
docker exec ollama ollama rm llama3.2

# Show model info
docker exec ollama ollama show llama3.2
```

### Test Ollama
```bash
# Simple test
docker exec ollama ollama run llama3.2 "Hello, how are you?"

# Via API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'

# List available models via API
curl http://localhost:11434/api/tags
```

### Ollama Logs
```bash
# View Ollama logs
docker-compose logs -f ollama

# Check Ollama status
curl http://localhost:11434/api/tags
```

---

## 🔢 Embedding Service Commands

### Health Check
```bash
# Check if service is running
curl http://localhost:8001/health

# Get service info
curl http://localhost:8001/
```

### Test Embeddings
```bash
# Generate embeddings
curl -X POST http://localhost:8001/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello world", "Test embedding"]
  }'
```

### Embedding Service Logs
```bash
# View logs
docker-compose logs -f embedding-service

# Restart if needed
docker-compose restart embedding-service
```

---

## 🗄️ Database Commands

### PostgreSQL Access
```bash
# Connect to PostgreSQL
docker exec -it ragdb psql -U raguser -d ragdb

# Run SQL query
docker exec ragdb psql -U raguser -d ragdb -c "SELECT * FROM users;"

# Backup database
docker exec ragdb pg_dump -U raguser ragdb > backup_$(date +%Y%m%d).sql

# Restore database
cat backup.sql | docker exec -i ragdb psql -U raguser -d ragdb
```

### Database Queries
```sql
-- Inside PostgreSQL shell

-- List tables
\dt

-- Describe table
\d users

-- Check vector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Count vectors
SELECT COUNT(*) FROM langchain_pg_embedding;

-- View connections
SELECT * FROM database_connections;

-- View query history
SELECT * FROM query_history ORDER BY created_at DESC LIMIT 10;
```

### Database Logs
```bash
# View PostgreSQL logs
docker-compose logs -f postgres
```

---

## 🌐 Backend API Commands

### Health Checks
```bash
# API documentation
curl http://localhost:8000/docs

# OpenAPI spec
curl http://localhost:8000/openapi.json

# Health check (if implemented)
curl http://localhost:8000/health
```

### Test API Endpoints
```bash
# List connections
curl http://localhost:8000/api/connections

# Get query history
curl http://localhost:8000/api/query/history

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### Backend Logs
```bash
# View backend logs
docker-compose logs -f backend

# Filter for errors
docker-compose logs backend | grep ERROR

# Follow specific patterns
docker-compose logs -f backend | grep "RAG"
```

---

## 🎨 Frontend Commands

### Access Frontend
```bash
# Open in browser
open http://localhost:3000  # Mac
start http://localhost:3000  # Windows
xdg-open http://localhost:3000  # Linux
```

### Frontend Logs
```bash
# View frontend logs
docker-compose logs -f frontend
```

---

## 🔧 Configuration Commands

### Environment Variables
```bash
# View current .env
cat .env

# Edit .env
nano .env  # Linux/Mac
notepad .env  # Windows

# Reload after changes
docker-compose down
docker-compose up -d
```

### Switch Models
```bash
# Edit .env
nano .env

# Change OLLAMA_MODEL
OLLAMA_MODEL=tinyllama  # or llama3.2, phi3, mistral

# Restart backend
docker-compose restart backend
```

### Switch Modes
```bash
# Edit .env
nano .env

# For self-hosted
USE_LOCAL_MODELS=true

# For cloud (OpenAI)
USE_LOCAL_MODELS=false
OPENAI_API_KEY=sk-...

# Restart
docker-compose restart backend
```

---

## 🐛 Debugging Commands

### Check Service Health
```bash
# All services
docker-compose ps

# Specific checks
curl http://localhost:3000  # Frontend
curl http://localhost:8000/docs  # Backend
curl http://localhost:8001/health  # Embeddings
curl http://localhost:11434/api/tags  # Ollama
```

### Inspect Containers
```bash
# Get container details
docker inspect backend

# Check container logs
docker logs backend

# Execute command in container
docker exec -it backend bash

# Check environment variables
docker exec backend env
```

### Resource Monitoring
```bash
# Real-time resource usage
docker stats

# Disk usage
docker system df

# Network inspection
docker network ls
docker network inspect <network-name>
```

### Troubleshooting
```bash
# Check for errors in all logs
docker-compose logs | grep -i error

# Check specific service errors
docker-compose logs backend | grep -i error

# View last 50 lines of all logs
docker-compose logs --tail=50

# Follow logs for debugging
docker-compose logs -f backend embedding-service ollama
```

---

## 🔄 Update & Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart with new images
docker-compose up -d

# Or do it all at once
git pull && docker-compose build && docker-compose up -d
```

### Update Models
```bash
# Pull latest model version
docker exec ollama ollama pull llama3.2

# Restart backend to use new model
docker-compose restart backend
```

### Clean Up Old Data
```bash
# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 💾 Backup & Restore

### Backup Database
```bash
# Full backup
docker exec ragdb pg_dump -U raguser ragdb > backup_$(date +%Y%m%d).sql

# Compressed backup
docker exec ragdb pg_dump -U raguser ragdb | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup specific table
docker exec ragdb pg_dump -U raguser -t users ragdb > users_backup.sql
```

### Restore Database
```bash
# Restore from backup
cat backup.sql | docker exec -i ragdb psql -U raguser -d ragdb

# Restore from compressed
gunzip -c backup.sql.gz | docker exec -i ragdb psql -U raguser -d ragdb
```

### Backup Volumes
```bash
# Backup PostgreSQL data
docker run --rm -v ragdb_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data

# Backup Ollama models
docker run --rm -v ragdb_ollama_data:/data -v $(pwd):/backup ubuntu tar czf /backup/ollama_backup.tar.gz /data
```

---

## 🚀 AWS Deployment Commands

### Connect to EC2
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<ec2-public-ip>
```

### Install Docker on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Deploy on EC2
```bash
# Clone repo
git clone <your-repo-url>
cd <repo-name>

# Configure
cp .env.example .env
nano .env

# Deploy
docker-compose up -d

# Download model
docker exec ollama ollama pull llama3.2
```

### Firewall Setup (EC2)
```bash
# Enable firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check status
sudo ufw status
```

---

## 📊 Monitoring Commands

### System Resources
```bash
# CPU and memory
top
htop  # if installed

# Disk space
df -h

# Docker stats
docker stats

# Specific container stats
docker stats backend
```

### Application Metrics
```bash
# Request count (from logs)
docker-compose logs backend | grep "POST /api/query" | wc -l

# Error count
docker-compose logs backend | grep ERROR | wc -l

# Recent errors
docker-compose logs --tail=100 backend | grep ERROR
```

### Network Monitoring
```bash
# Check open ports
netstat -tulpn

# Check Docker networks
docker network ls

# Inspect network
docker network inspect <network-name>
```

---

## 🔐 Security Commands

### SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Password Management
```bash
# Generate strong password
openssl rand -base64 32

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Security Audit
```bash
# Check for security updates
sudo apt update
sudo apt list --upgradable

# Update system
sudo apt upgrade -y

# Check Docker security
docker scan backend  # if Docker Scout is available
```

---

## 📝 Quick Reference

### Most Used Commands
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop everything
docker-compose down

# Check status
docker-compose ps

# Pull new model
docker exec ollama ollama pull llama3.2
```

### Emergency Commands
```bash
# Stop everything immediately
docker-compose down

# Force rebuild everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check what's wrong
docker-compose ps
docker-compose logs --tail=100
```

---

## 🎯 Pro Tips

### Aliases (Add to ~/.bashrc or ~/.zshrc)
```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dcr='docker-compose restart'

# Ollama shortcuts
alias ollama-list='docker exec ollama ollama list'
alias ollama-pull='docker exec ollama ollama pull'

# Logs shortcuts
alias logs-backend='docker-compose logs -f backend'
alias logs-ollama='docker-compose logs -f ollama'
alias logs-embed='docker-compose logs -f embedding-service'
```

### Watch Commands
```bash
# Watch container status
watch -n 2 'docker-compose ps'

# Watch resource usage
watch -n 2 'docker stats --no-stream'

# Watch logs for errors
watch -n 5 'docker-compose logs --tail=20 backend | grep ERROR'
```

---

**Save this file for quick reference!** 📌
