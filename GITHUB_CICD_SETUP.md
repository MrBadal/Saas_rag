# GitHub Actions CI/CD Setup Guide

This guide walks you through setting up automated CI/CD pipelines with GitHub Actions to deploy your SaaS RAG application to AWS EC2.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create GitHub Repository](#step-1-create-github-repository)
4. [Step 2: AWS IAM User Setup](#step-2-aws-iam-user-setup)
5. [Step 3: EC2 Instance Preparation](#step-3-ec2-instance-preparation)
6. [Step 4: GitHub Secrets Configuration](#step-4-github-secrets-configuration)
7. [Step 5: Push and Deploy](#step-5-push-and-deploy)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────┐     Push to main      ┌──────────────────┐
│   Developer     │ ────────────────────> │  GitHub Actions  │
│   (Your PC)     │                       │    (CI/CD)       │
└─────────────────┘                       └────────┬─────────┘
                                                   │
                          ┌────────────────────────┘
                          │ SSH + AWS API
                          ▼
                   ┌──────────────────┐
                   │   AWS EC2        │
                   │  (t2.micro)      │
                   │  Ubuntu 22.04    │
                   └────────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │Backend  │   │Frontend │   │Ollama   │
        │:8000    │   │:3000    │   │:11434   │
        └─────────┘   └─────────┘   └─────────┘
```

**Deployment Flow:**
1. Developer pushes code to `main` branch
2. GitHub Actions triggers automatically
3. Tests are run (Python linting, Node.js build)
4. On success, GitHub Actions connects to EC2 via SSH
5. Code is pulled on EC2
6. Docker containers are rebuilt and restarted
7. Health checks verify deployment

---

## Prerequisites

- AWS Account (Free Tier eligible)
- GitHub account
- Existing EC2 instance running Ubuntu 22.04
- Your source code ready for deployment

---

## Step 1: Create GitHub Repository

### Option A: Create New Repository on GitHub

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name it: `SaaS_rag` (or your preferred name)
4. Choose "Private" (recommended for your application)
5. Don't initialize with README (we have our own)
6. Click "Create repository"

### Option B: Initialize Local Repository and Push

Open terminal in your project directory and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - SaaS RAG application"

# Add remote repository (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/SaaS_rag.git

# Push to main branch
git branch -M main
git push -u origin main
```

### Verify Repository

```bash
# Check remote URL
git remote -v

# Should show:
# origin  https://github.com/YOUR_USERNAME/SaaS_rag.git (fetch)
# origin  https://github.com/YOUR_USERNAME/SaaS_rag.git (push)
```

---

## Step 2: AWS IAM User Setup

We need to create an IAM user with limited permissions for GitHub Actions.

### 2.1 Create IAM User

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → "Create user"
3. User name: `github-actions-deploy`
4. Click "Next"

### 2.2 Set Permissions

Choose "Attach policies directly" and add:

**Policy 1: AmazonEC2ReadOnlyAccess** (for describing EC2 instances)

**Policy 2: Create Inline Policy** with the following JSON:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus"
            ],
            "Resource": "*"
        }
    ]
}
```

Click "Next" → "Create user"

### 2.3 Create Access Keys

1. Click on the newly created user
2. Go to "Security credentials" tab
3. Scroll to "Access keys" → "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Check the confirmation box → "Next"
6. Add description: "GitHub Actions CI/CD"
7. Click "Create access key"
8. **IMPORTANT**: Download the `.csv` file or copy both:
   - Access key ID
   - Secret access key

**⚠️ WARNING**: You cannot view the secret access key again after this step!

---

## Step 3: EC2 Instance Preparation

### 3.1 Connect to Your EC2 Instance

```bash
# Using your existing .pem file
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 3.2 Run Setup Script

```bash
# Clone or create the repository first
git clone https://github.com/YOUR_USERNAME/SaaS_rag.git ~/SaaS_rag
cd ~/SaaS_rag

# Make scripts executable
chmod +x scripts/*.sh

# Run the EC2 setup script
./scripts/setup-ec2.sh
```

This script will:
- Install Docker and Docker Compose
- Install Git and other tools
- Create 2GB swap space (essential for t2.micro)
- Configure system settings

### 3.3 Logout and Login Again

```bash
exit
# Wait a few seconds
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 3.4 Get SSH Key for GitHub Actions

```bash
# Display the authorized_keys content
cat ~/.ssh/authorized_keys
```

Copy this entire line (it starts with `ssh-rsa` or `ssh-ed25519`).

---

## Step 4: GitHub Secrets Configuration

### 4.1 Navigate to GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" tab
3. In left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"

### 4.2 Add Required Secrets

Add these secrets one by one:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | From Step 2.3 |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | From Step 2.3 |
| `AWS_REGION` | Your AWS region | e.g., `us-east-1` |
| `EC2_HOST` | Your EC2 public IP | From AWS Console |
| `EC2_USERNAME` | `ubuntu` | Default for Ubuntu |
| `EC2_SSH_KEY` | SSH private key | From Step 3.4 |
| `SECRET_KEY` | Random string | Generate below |

### 4.3 Generate SECRET_KEY

On your local machine or EC2:

```bash
# Generate a secure random key
openssl rand -hex 32
```

Copy the output and add it as `SECRET_KEY` in GitHub Secrets.

### 4.4 Verify All Secrets

Your GitHub Secrets should look like this:

```
Repository secrets (7)
├── AWS_ACCESS_KEY_ID: AKIA...
├── AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI...
├── AWS_REGION: us-east-1
├── EC2_HOST: 3.91.123.45
├── EC2_USERNAME: ubuntu
├── EC2_SSH_KEY: ssh-rsa AAAAB3NzaC1...
└── SECRET_KEY: a1b2c3d4e5f6...
```

---

## Step 5: Push and Deploy

### 5.1 Push CI/CD Files to GitHub

```bash
# Add all new files
git add .

# Commit
git commit -m "Add CI/CD pipeline with GitHub Actions"

# Push to main
git push origin main
```

### 5.2 Monitor Deployment

1. Go to your GitHub repository
2. Click "Actions" tab
3. You should see the workflow running
4. Click on the workflow run to see details

### 5.3 Verify Deployment

Once the workflow completes successfully:

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Check container status
cd ~/SaaS_rag
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5.4 Access Your Application

- **Frontend**: http://YOUR_EC2_IP:3000
- **Backend API Docs**: http://YOUR_EC2_IP:8000/docs
- **Embedding Service**: http://YOUR_EC2_IP:8001/health

---

## Troubleshooting

### Issue 1: GitHub Actions Fails to Connect to EC2

**Error**: `Permission denied (publickey)`

**Solution**:
```bash
# On EC2, ensure proper permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Verify the key in GitHub secrets matches
cat ~/.ssh/authorized_keys
```

### Issue 2: Docker Permission Denied

**Error**: `Got permission denied while trying to connect to the Docker daemon`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker ubuntu

# Logout and login again
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Verify
docker ps
```

### Issue 3: Out of Memory (OOM)

**Error**: Containers keep restarting or failing

**Solution**:
```bash
# Check memory usage
free -h

# Check if swap is enabled
swapon --show

# If no swap, create it
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue 4: Model Not Found

**Error**: Ollama model not available

**Solution**:
```bash
# Manually pull the model
docker exec ollama ollama pull llama3.2

# Or use a smaller model
docker exec ollama ollama pull tinyllama
```

### Issue 5: GitHub Actions Workflow Not Triggering

**Check**:
1. Is the file in `.github/workflows/deploy.yml`?
2. Did you push to `main` or `master` branch?
3. Check "Actions" tab → "Workflows" → enable if disabled

---

## Security Best Practices

1. **Rotate Secrets Regularly**: Change AWS keys every 90 days
2. **Use Branch Protection**: Require PR reviews before merging to main
3. **Limit IAM Permissions**: The IAM user only needs EC2 read access
4. **Monitor Logs**: Check CloudTrail for unusual activity
5. **Enable 2FA**: On your GitHub and AWS accounts

---

## Next Steps

1. **Set up Branch Protection**:
   - Go to Settings → Branches
   - Add rule for `main` branch
   - Require pull request reviews

2. **Add Tests**: Enhance the CI pipeline with actual tests

3. **Add Notifications**: Get Slack/Email notifications on deployment

4. **Set up Monitoring**: Use CloudWatch to monitor EC2 resources

---

## Quick Reference Commands

```bash
# Manual deployment (if needed)
cd ~/SaaS_rag && ./scripts/deploy.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Check resource usage
docker stats

# Update and redeploy
git pull && ./scripts/deploy.sh
```

---

## Support

If you encounter issues:
1. Check GitHub Actions logs for detailed error messages
2. SSH into EC2 and check container logs
3. Verify all secrets are correctly set
4. Ensure EC2 security group allows ports 3000 and 8000