# Deployment Guide

## Local Development

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector extension

### Quick Start

1. **Clone and setup environment:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

2. **Start with Docker Compose:**
```bash
docker-compose up -d
```

3. **Initialize database:**
```bash
docker-compose exec backend python -c "from app.models.database import init_db; init_db()"
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## AWS Deployment

### Architecture
- **Compute**: ECS Fargate (or EC2 t2.micro for free tier)
- **Database**: RDS PostgreSQL with pgvector
- **Storage**: S3 for static assets
- **Load Balancer**: ALB
- **Secrets**: AWS Secrets Manager

### Step 1: Setup RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier rag-platform-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username ragadmin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

Enable pgvector extension:
```sql
CREATE EXTENSION vector;
```

### Step 2: Build and Push Docker Images

```bash
# Backend
docker build -t rag-platform-backend ./backend
docker tag rag-platform-backend:latest YOUR_ECR_REPO/backend:latest
docker push YOUR_ECR_REPO/backend:latest

# Frontend
docker build -t rag-platform-frontend ./frontend
docker tag rag-platform-frontend:latest YOUR_ECR_REPO/frontend:latest
docker push YOUR_ECR_REPO/frontend:latest
```

### Step 3: Deploy to ECS

Create ECS task definitions and services using the AWS Console or CLI.

### Step 4: Configure Environment Variables

Store in AWS Secrets Manager:
- `OPENAI_API_KEY`
- `DATABASE_URL`
- `SECRET_KEY`

### Step 5: Setup CloudWatch Monitoring

Enable logging and create alarms for:
- API errors
- Database connection failures
- High latency

## Terraform Deployment (Recommended)

See `terraform/` directory for infrastructure as code.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Rotate SECRET_KEY
- [ ] Encrypt database connection strings
- [ ] Enable AWS WAF
- [ ] Setup VPC with private subnets
- [ ] Enable CloudTrail logging
- [ ] Configure security groups properly
- [ ] Use IAM roles instead of access keys
- [ ] Enable RDS encryption at rest
- [ ] Setup backup policies

## Monitoring

### Key Metrics
- API response time
- Database query performance
- Vector search latency
- LLM API call success rate
- User query volume

### CloudWatch Dashboards
Create dashboards for:
- Application health
- Database performance
- Cost tracking
- User activity

## Scaling Considerations

### Horizontal Scaling
- Use ECS auto-scaling based on CPU/memory
- Add read replicas for database
- Implement caching (Redis/ElastiCache)

### Vertical Scaling
- Upgrade RDS instance class
- Increase ECS task resources

## Cost Optimization

### Free Tier Usage
- EC2 t2.micro (750 hours/month)
- RDS db.t2.micro (750 hours/month)
- 5GB S3 storage
- 1M Lambda requests

### Cost Reduction Tips
- Use spot instances for non-critical workloads
- Implement request caching
- Optimize LLM API calls
- Use S3 lifecycle policies
- Enable RDS auto-pause for dev environments

## Troubleshooting

### Common Issues

**Database connection fails:**
- Check security group rules
- Verify DATABASE_URL format
- Ensure pgvector extension is installed

**Vector store errors:**
- Verify pgvector is properly installed
- Check table permissions
- Review embedding dimensions

**LLM API errors:**
- Validate OPENAI_API_KEY
- Check rate limits
- Monitor API quota

## Backup & Recovery

### Database Backups
- Enable automated RDS backups (7-35 days retention)
- Create manual snapshots before major changes
- Test restore procedures regularly

### Application State
- Store user data in RDS (automatically backed up)
- Vector embeddings can be regenerated from source data
