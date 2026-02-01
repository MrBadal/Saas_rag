# CI/CD Architecture Documentation

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DEVELOPER WORKSTATION                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Local Development                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │   │
│  │  │   Code      │  │   Test      │  │   Commit    │                     │   │
│  │  │   Editor    │  │   Locally   │  │   Changes   │                     │   │
│  │  └──────┬──────┘  └─────────────┘  └──────┬──────┘                     │   │
│  │         │                                   │                           │   │
│  │         └───────────────────────────────────┘                           │   │
│  │                         │                                               │   │
│  │                         ▼                                               │   │
│  │              git push origin main                                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTPS (Port 443)
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GITHUB PLATFORM                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  GitHub Repository                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │   │
│  │  │   Source    │  │   GitHub    │  │   Secrets   │                     │   │
│  │  │   Code      │  │   Actions   │  │   Storage   │                     │   │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────┘                     │   │
│  │         │                │                                              │   │
│  │         └────────────────┘                                              │   │
│  │                      │                                                  │   │
│  │                      ▼                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    GitHub Actions Workflow                       │   │   │
│  │  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │   │   │
│  │  │  │  Test    │───>│  Build   │───>│  Deploy  │───>│  Verify  │  │   │   │
│  │  │  │  Job     │    │  Images  │    │  to EC2  │    │  Health  │  │   │   │
│  │  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ SSH (Port 22) + AWS API
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD (Free Tier)                               │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  EC2 Instance (t2.micro)                                                 │   │
│  │  Ubuntu 22.04 LTS | 1 vCPU | 1 GB RAM | 30 GB SSD                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Docker Environment                            │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │   │
│  │  │  │  Nginx      │  │  Frontend   │  │   Backend   │             │   │   │
│  │  │  │  (Reverse   │  │  React App  │  │   FastAPI   │             │   │   │
│  │  │  │   Proxy)    │  │   :3000     │  │    :8000    │             │   │   │
│  │  │  │   :80/443   │  │             │  │             │             │   │   │
│  │  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │   │   │
│  │  │         │                │                │                      │   │   │
│  │  │         └────────────────┴────────────────┘                      │   │   │
│  │  │                          │                                       │   │   │
│  │  │                          ▼                                       │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │   │
│  │  │  │  PostgreSQL │  │  Embedding  │  │   Ollama    │             │   │   │
│  │  │  │  + pgvector │  │   Service   │  │   (LLM)     │             │   │   │
│  │  │  │   :5432     │  │    :8001    │  │   :11434    │             │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                              │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  Volumes & Data                                                  │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │   │
│  │  │  │  postgres_  │  │  ollama_    │  │  app_code   │             │   │   │
│  │  │  │   data      │  │   data      │  │  (bind mount)│             │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Security Group Configuration                                            │   │
│  │  ┌─────────────┬─────────────┬─────────────────────────────────────┐   │   │
│  │  │   Type      │   Port      │            Source                   │   │   │
│  │  ├─────────────┼─────────────┼─────────────────────────────────────┤   │   │
│  │  │   SSH       │   22        │  My IP (Your local machine)         │   │   │
│  │  │   HTTP      │   80        │  0.0.0.0/0 (Anywhere)               │   │   │
│  │  │   HTTPS     │   443       │  0.0.0.0/0 (Anywhere)               │   │   │
│  │  │   Custom    │   3000      │  0.0.0.0/0 (Frontend access)        │   │   │
│  │  │   Custom    │   8000      │  0.0.0.0/0 (Backend API)            │   │   │
│  │  └─────────────┴─────────────┴─────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTP/HTTPS
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              END USERS                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Web       │  │   API       │  │  Database   │  │  LLM Chat   │           │
│  │  Browser    │  │  Clients    │  │  Queries    │  │  Interface  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Request Flow:
──────────────────

User Browser
     │
     │ HTTP Request
     ▼
EC2:3000 (Frontend Container)
     │
     │ API Call
     ▼
EC2:8000 (Backend Container)
     │
     ├────────────────┬────────────────┐
     │                │                │
     ▼                ▼                ▼
Postgres:5432  Embedding:8001   Ollama:11434
(Database)     (Vector Search)   (LLM Model)
     │                │                │
     └────────────────┴────────────────┘
                      │
                      ▼
              Response to User
```

## CI/CD Pipeline Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Push   │────>│  Test   │────>│  Build  │────>│ Deploy  │────>│ Verify  │
│  Code   │     │   Job   │     │  Images │     │  to EC2 │     │  Health │
└─────────┘     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
                     │               │               │               │
                     ▼               ▼               ▼               ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
              │Python    │    │Backend   │    │SSH to    │    │HTTP      │
              │Linting   │    │Dockerfile│    │EC2       │    │Health    │
              │          │    │          │    │          │    │Checks    │
              ├──────────┤    ├──────────┤    ├──────────┤    ├──────────┤
              │Node.js   │    │Frontend  │    │Git Pull  │    │Backend   │
              │Build     │    │Dockerfile│    │          │    │API       │
              │          │    │          │    ├──────────┤    │          │
              └──────────┘    │Embedding │    │Docker    │    └──────────┘
                              │Dockerfile│    │Compose   │
                              └──────────┘    │Up        │
                                              └──────────┘
```

## GitHub Actions Workflow Structure

```
.github/workflows/deploy.yml
│
├── Trigger: push to main/master
│
├── Job 1: test
│   ├── Checkout code
│   ├── Setup Python 3.11
│   ├── Setup Node.js 18
│   ├── Install Python dependencies
│   ├── Run Python linting (flake8)
│   ├── Install Node.js dependencies
│   └── Run frontend build test
│
└── Job 2: deploy (depends on: test)
    ├── Checkout code
    ├── Configure AWS credentials
    ├── Setup SSH key
    ├── Deploy to EC2 via SSH
    │   ├── Pull latest code
    │   ├── Create .env file
    │   ├── Build containers
    │   ├── Start services
    │   └── Cleanup old images
    └── Verify deployment (HTTP checks)
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: GitHub                                                 │
│  ├── Repository Secrets (Encrypted)                              │
│  ├── Branch Protection Rules                                     │
│  └── Access Control (Collaborators)                              │
│                                                                  │
│  Layer 2: AWS IAM                                                │
│  ├── Dedicated IAM User (github-actions-deploy)                  │
│  ├── Minimal Permissions (EC2 read-only)                         │
│  └── Access Keys (Rotatable)                                     │
│                                                                  │
│  Layer 3: EC2 Security                                           │
│  ├── Security Groups (Port restrictions)                         │
│  ├── SSH Key Authentication                                      │
│  └── OS-level Security Updates                                   │
│                                                                  │
│  Layer 4: Application                                            │
│  ├── Secret Key for JWT/API                                      │
│  ├── Environment-based Configuration                             │
│  └── Container Isolation                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Resource Allocation (t2.micro - 1GB RAM)

```
┌────────────────────────────────────────────────────────────┐
│                    MEMORY ALLOCATION                        │
│                    Total: 1 GB RAM                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Swap Space (2GB)                                   │  │
│  │  ├─ Overflow from RAM                               │  │
│  │  └─ Prevents OOM kills                              │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Container Memory Limits                            │  │
│  │  ├─ PostgreSQL:        512 MB                       │  │
│  │  ├─ Embedding Service: 1 GB                         │  │
│  │  ├─ Ollama:            1.5 GB (uses swap)           │  │
│  │  ├─ Backend:           512 MB                       │  │
│  │  └─ Frontend:          512 MB                       │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Note: Containers use swap when exceeding RAM limits       │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Network Ports

```
┌────────────────────────────────────────────────────────────┐
│  Port    │ Service        │ Access          │ Purpose       │
├────────────────────────────────────────────────────────────┤
│  22      │ SSH            │ Your IP only    │ Admin access  │
│  80      │ HTTP           │ Public          │ Nginx (opt)   │
│  443     │ HTTPS          │ Public          │ Nginx (opt)   │
│  3000    │ Frontend       │ Public          │ React App     │
│  8000    │ Backend API    │ Public          │ FastAPI       │
│  8001    │ Embedding      │ Internal        │ Vector Search │
│  5432    │ PostgreSQL     │ Internal        │ Database      │
│  11434   │ Ollama         │ Internal        │ LLM Service   │
└────────────────────────────────────────────────────────────┘
```

## File Structure on EC2

```
/home/ubuntu/SaaS_rag/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD workflow (not used on EC2)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── models/
│       └── services/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.js
│       └── components/
├── scripts/
│   ├── deploy.sh               # Main deployment script
│   └── setup-ec2.sh            # Initial setup script
├── docker-compose.prod.yml     # Production compose file
├── .env                        # Environment variables (created by CI/CD)
└── .env.example                # Environment template
```

## Deployment Triggers

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT TRIGGERS                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Automatic Triggers:                                         │
│  ├─ Push to main branch    ──>  Full CI/CD Pipeline         │
│  └─ Pull Request to main   ──>  Test Job Only               │
│                                                              │
│  Manual Triggers (via GitHub Actions):                      │
│  ├─ Workflow Dispatch      ──>  Run workflow manually       │
│  └─ Re-run failed jobs     ──>  Retry deployment            │
│                                                              │
│  Manual Triggers (on EC2):                                  │
│  └─ ./scripts/deploy.sh    ──>  Local deployment            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Backup and Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Persistent Volumes:                                         │
│  ├─ postgres_data  ──>  Database files                      │
│  │                      (survives container restart)        │
│  └─ ollama_data    ──>  LLM model files                     │
│                         (survives container restart)        │
│                                                              │
│  Non-Persistent:                                             │
│  ├─ Application code  ──>  Rebuilt from Git on deploy       │
│  └─ Container layers  ──>  Rebuilt on each deployment       │
│                                                              │
│  Backup Strategy:                                            │
│  ├─ Database: Use pg_dump for periodic backups              │
│  └─ Models: Re-download from Ollama if needed               │
│                                                              │
└─────────────────────────────────────────────────────────────┘