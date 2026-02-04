# Backend Connectivity Issue - Fix Plan

## Problem Summary

The frontend is unable to connect to the backend API in the deployed environment because the `REACT_APP_API_URL` environment variable is not being set correctly during the Docker build process.

### Root Cause

In `docker-compose.prod.yml`, the frontend service uses:
```yaml
environment:
  - REACT_APP_API_URL=http://${EC2_PUBLIC_IP:-localhost}:8000
```

However, `EC2_PUBLIC_IP` is not defined anywhere, so it defaults to `localhost`. When users access the app via the EC2 public IP (13.233.168.67), the frontend tries to call `http://localhost:8000` from the browser, which fails because the backend isn't running on the user's machine.

## Solution

The fix involves three coordinated changes to ensure the EC2 host/IP is properly passed through the build process:

### 1. Update `docker-compose.prod.yml`

Add build arguments to the frontend service so the API URL can be passed at build time:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      - REACT_APP_API_URL=http://${EC2_HOST:-localhost}:8000
  container_name: frontend
  ports:
    - "3000:3000"
  depends_on:
    - backend
  restart: unless-stopped
```

### 2. Update `frontend/Dockerfile`

Modify the Dockerfile to accept the build argument and make it available as an environment variable during the build:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Accept build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### 3. Update `.github/workflows/deploy.yml`

Modify the deployment script to export `EC2_HOST` from the GitHub secret before running docker-compose:

```yaml
- name: Deploy to EC2
  run: |
    ssh -i ~/.ssh/ec2_key.pem ${{ secrets.EC2_USERNAME }}@${{ secrets.EC2_HOST }} << 'EOF'
      set -e
      
      echo "=== Starting Deployment ==="
      
      # Navigate to app directory
      cd $HOME/SaaS_rag
      
      echo "=== Pulling latest code ==="
      git fetch origin
      git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
      
      echo "=== Creating production environment file ==="
      cat > .env << ENVFILE
      # ... existing env vars ...
      ENVFILE
      
      # Export EC2_HOST for docker-compose
      export EC2_HOST=${{ secrets.EC2_HOST }}
      
      echo "=== Building and starting containers ==="
      docker-compose -f docker-compose.prod.yml down --remove-orphans || true
      docker-compose -f docker-compose.prod.yml pull
      docker-compose -f docker-compose.prod.yml build --no-cache
      docker-compose -f docker-compose.prod.yml up -d
      
      # ... rest of deployment ...
    EOF
```

## How It Works

1. **GitHub Actions** exports `EC2_HOST` (e.g., `13.233.168.67`) from secrets
2. **docker-compose.prod.yml** uses this variable to set the build argument
3. **frontend/Dockerfile** receives the build argument and sets it as an environment variable
4. **React** picks up `REACT_APP_API_URL` during the build and embeds it in the static files
5. **Frontend** now calls `http://13.233.168.67:8000` instead of `localhost`

## Verification Steps After Deployment

1. Access the frontend at `http://13.233.168.67:3000`
2. Open browser DevTools (F12) → Network tab
3. Try to log in or register
4. Check that API calls are going to `http://13.233.168.67:8000/api/...` instead of `localhost`

## Alternative: Using a Domain Name

If you add a custom domain in the future, simply update the `EC2_HOST` secret in GitHub to use the domain name instead of the IP (e.g., `api.yourdomain.com`).
