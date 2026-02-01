# AWS Free Tier Deployment Guide - Self-Hosted RAG

This guide shows how to deploy the **completely self-hosted RAG system** on AWS Free Tier with **zero external API costs**.

## 🎯 What You Get

- ✅ **100% Free** - No OpenAI or external API costs
- ✅ **Self-Hosted** - All models run on your infrastructure
- ✅ **AWS Free Tier** - 750 hours/month of t2.micro EC2
- ✅ **Plug & Play** - Users just provide database connection strings

---

## 📋 Prerequisites

1. AWS Account (Free Tier eligible)
2. Basic Linux/SSH knowledge
3. Domain name (optional, for HTTPS)

---

## 🚀 Deployment Steps

### Step 1: Launch EC2 Instance

1. **Go to EC2 Dashboard**
   - Region: Choose closest to your users (e.g., us-east-1)

2. **Launch Instance**
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: t2.micro (1 vCPU, 1GB RAM) - Free tier
   - **Storage**: 30 GB gp3 (Free tier includes 30GB)
   - **Security Group**: Create new with these rules:
     - SSH (22) - Your IP only
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
     - Custom TCP (8000) - 0.0.0.0/0 (Backend API)
     - Custom TCP (3000) - 0.0.0.0/0 (Frontend)

3. **Create/Download Key Pair**
   - Save the `.pem` file securely

4. **Launch Instance**

---

### Step 2: Connect to Instance

```bash
# Make key file secure
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

---

### Step 3: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Logout and login again for group changes
exit
# SSH back in
```

---

### Step 4: Clone/Upload Your Application

**Option A: From Git Repository**
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

**Option B: Upload via SCP**
```bash
# From your local machine
scp -i your-key.pem -r /path/to/project ubuntu@<ec2-ip>:~/
```

---

### Step 5: Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit configuration
nano .env
```

Update these values:
```env
USE_LOCAL_MODELS=true
EMBEDDING_SERVICE_URL=http://embedding-service:8001
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
DATABASE_URL=postgresql://raguser:ragpass@postgres:5432/ragdb
SECRET_KEY=<generate-strong-random-key>
```

---

### Step 6: Deploy Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

### Step 7: Download Ollama Model

```bash
# Pull the LLM model (one-time, ~2GB download)
docker exec ollama ollama pull llama3.2

# Verify model is ready
docker exec ollama ollama list
```

**Alternative smaller models for t2.micro:**
- `phi3` (3.8GB) - Microsoft's efficient model
- `tinyllama` (637MB) - Ultra-lightweight
- `gemma:2b` (1.4GB) - Google's small model

---

### Step 8: Initialize Database

```bash
# Access backend container
docker exec -it backend bash

# Run database migrations (if you have them)
# python -m alembic upgrade head

# Or manually create tables
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"

exit
```

---

### Step 9: Test the System

```bash
# Check all services are running
curl http://localhost:8000/docs  # Backend API docs
curl http://localhost:8001/health  # Embedding service
curl http://localhost:11434/api/tags  # Ollama models
curl http://localhost:3000  # Frontend
```

---

### Step 10: Configure Nginx (Optional but Recommended)

```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/rag-app
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name <your-domain-or-ip>;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Security Hardening

### 1. Enable Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Secure PostgreSQL
- Change default passwords in `.env`
- Don't expose port 5432 externally

### 3. Enable HTTPS (Free with Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ollama
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
git pull  # or upload new files
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
docker exec ragdb pg_dump -U raguser ragdb > backup_$(date +%Y%m%d).sql
```

---

## 💰 Cost Breakdown (AWS Free Tier)

| Resource | Free Tier | Cost After Free Tier |
|----------|-----------|---------------------|
| EC2 t2.micro | 750 hrs/month (1 year) | ~$8.50/month |
| EBS Storage (30GB) | 30 GB (1 year) | ~$3/month |
| Data Transfer | 15 GB/month | $0.09/GB |
| **Total** | **$0/month (Year 1)** | **~$12/month after** |

**Note**: All AI processing is local - no OpenAI/API costs!

---

## 🎯 Performance Optimization for t2.micro

### 1. Use Smaller Models
```bash
# Instead of llama3.2 (2GB), use:
docker exec ollama ollama pull tinyllama  # 637MB
docker exec ollama ollama pull phi3:mini  # 2.3GB
```

### 2. Enable Swap (for 1GB RAM)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Limit Docker Memory
Update `docker-compose.yml`:
```yaml
services:
  ollama:
    mem_limit: 512m
  embedding-service:
    mem_limit: 256m
```

---

## 🔧 Troubleshooting

### Issue: Out of Memory
**Solution**: Use smaller models or add swap space

### Issue: Slow Response Times
**Solution**: 
- Use `tinyllama` or `phi3:mini`
- Reduce vector search `k` parameter
- Enable response caching

### Issue: Ollama Not Responding
```bash
docker-compose restart ollama
docker exec ollama ollama list
```

### Issue: Embedding Service Fails
```bash
docker-compose logs embedding-service
docker-compose restart embedding-service
```

---

## 📈 Scaling Beyond Free Tier

When you outgrow t2.micro:

1. **Upgrade to t3.small** ($15/month)
   - 2 vCPU, 2GB RAM
   - Run larger models (llama3.2, mistral)

2. **Use RDS for PostgreSQL** (optional)
   - Managed database
   - Automatic backups

3. **Add Load Balancer** (for high traffic)
   - Application Load Balancer
   - Auto-scaling group

---

## ✅ Verification Checklist

- [ ] EC2 instance running
- [ ] Docker & Docker Compose installed
- [ ] All containers running (`docker-compose ps`)
- [ ] Ollama model downloaded
- [ ] Database initialized
- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Embedding service healthy
- [ ] Test query works end-to-end

---

## 🎉 Success!

Your self-hosted RAG system is now running on AWS Free Tier with:
- ✅ Zero external API costs
- ✅ Complete data privacy
- ✅ Full control over models
- ✅ Plug-and-play for users

**Next Steps:**
1. Test with real database connections
2. Monitor resource usage
3. Set up automated backups
4. Configure domain and HTTPS
5. Share with users!

---

## 📚 Additional Resources

- [Ollama Models](https://ollama.ai/library)
- [Sentence Transformers](https://www.sbert.net/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [AWS Free Tier Details](https://aws.amazon.com/free/)
