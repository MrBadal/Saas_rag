# AWS Deployment Troubleshooting Guide

## 🔴 Issue: Frontend Not Connecting to Backend

**Public IP**: 13.233.168.67

### Quick Diagnosis Steps

#### 1. Check if Backend is Running
```bash
# SSH into your AWS instance
ssh -i your-key.pem ubuntu@13.233.168.67

# Check if backend container is running
docker ps | grep backend

# Check backend logs
docker logs backend

# Test backend health endpoint
curl http://localhost:8000/health
```

**Expected Output**:
```json
{"status": "healthy"}
```

#### 2. Check AWS Security Groups
Ensure your AWS Security Group allows inbound traffic on:
- Port 80 (HTTP) - for frontend
- Port 8000 (Backend API) - for backend
- Port 3000 (Development frontend) - optional

**AWS Console Steps**:
1. Go to EC2 → Security Groups
2. Find your instance's security group
3. Edit Inbound Rules:
   ```
   Type: HTTP, Port: 80, Source: 0.0.0.0/0
   Type: Custom TCP, Port: 8000, Source: 0.0.0.0/0
   Type: Custom TCP, Port: 3000, Source: 0.0.0.0/0 (if needed)
   ```

#### 3. Verify Frontend API URL
Check what API URL the frontend is using:

**Option A: Check in browser**
1. Open browser console (F12)
2. Look for log: "API URL: http://..."

**Option B: Check in container**
```bash
# Check frontend environment
docker exec frontend env | grep REACT_APP_API_URL
```

**Should show**: `REACT_APP_API_URL=http://13.233.168.67:8000`

#### 4. Test Direct Backend Access
From your local machine:
```bash
curl http://13.233.168.67:8000/health
```

If this fails, the backend is not accessible externally.

---

## 🔧 Fixes

### Fix 1: Rebuild Frontend with Correct API URL

```bash
# SSH into AWS instance
ssh -i your-key.pem ubuntu@13.233.168.67

# Navigate to project
cd /path/to/your/project

# Stop and remove frontend container
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm frontend

# Rebuild with correct IP
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

### Fix 2: Update docker-compose.prod.yml

Ensure your `docker-compose.prod.yml` has the correct IP:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      - REACT_APP_API_URL=http://13.233.168.67:8000  # Your actual IP
  environment:
    - REACT_APP_API_URL=http://13.233.168.67:8000
```

### Fix 3: Hardcode API URL in client.js (Temporary Fix)

Edit `frontend/src/api/client.js`:

```javascript
// Change from:
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// To:
const API_URL = 'http://13.233.168.67:8000';
```

Then rebuild:
```bash
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

---

## 🔍 Debugging Commands

### Check All Containers Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View All Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

### Check Network Connectivity
```bash
# From frontend container, try to reach backend
docker exec frontend ping backend

# Test backend from frontend
docker exec frontend curl http://backend:8000/health
```

### Check Environment Variables
```bash
# Backend env
docker exec backend env | grep -E '(DATABASE|API|URL)'

# Frontend env
docker exec frontend env | grep REACT_APP
```

---

## ✅ Complete Redeployment Steps

If nothing else works, do a clean redeployment:

```bash
# 1. SSH to server
ssh -i your-key.pem ubuntu@13.233.168.67

# 2. Navigate to project
cd ~/SaaS_rag  # or wherever your project is

# 3. Pull latest changes
git pull origin main

# 4. Stop all containers
docker-compose -f docker-compose.prod.yml down

# 5. Remove old images (optional but recommended)
docker system prune -a --volumes

# 6. Update docker-compose.prod.yml with correct IP
# Edit the file and ensure REACT_APP_API_URL=http://13.233.168.67:8000

# 7. Rebuild everything
docker-compose -f docker-compose.prod.yml build --no-cache

# 8. Start services
docker-compose -f docker-compose.prod.yml up -d

# 9. Check status
docker-compose -f docker-compose.prod.yml ps

# 10. Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🌐 Testing the Connection

### Test 1: Backend Health
```bash
curl http://13.233.168.67:8000/health
```

### Test 2: Frontend Access
Open browser and go to:
```
http://13.233.168.67
```

Check for:
- ✅ "Backend connected successfully" message
- ❌ Red error box with connection troubleshooting

### Test 3: API Connection from Browser
Open browser console (F12) and check:
- Network tab for failed requests
- Console tab for error messages
- Should see: "API URL: http://13.233.168.67:8000"

---

## 🚨 Common Issues & Solutions

### Issue 1: "No response from server"
**Cause**: Backend not running or not accessible
**Solution**: 
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Issue 2: "Connection refused"
**Cause**: Security group blocking port 8000
**Solution**: Update AWS Security Group inbound rules

### Issue 3: "CORS error"
**Cause**: Backend CORS not configured correctly
**Solution**: Already fixed in main.py (allows all origins)

### Issue 4: Frontend shows "API URL: http://localhost:8000"
**Cause**: Environment variable not set during build
**Solution**: Rebuild frontend with correct IP

---

## 📞 Still Having Issues?

Check these logs and provide them:

1. **Backend logs**: `docker logs backend`
2. **Frontend logs**: `docker logs frontend`
3. **Browser console errors**: Screenshot of F12 console
4. **Network tab**: Screenshot of failed requests

**Quick Command to Get All Logs**:
```bash
docker-compose -f docker-compose.prod.yml logs > deployment-logs.txt 2>&1
```

Then share the `deployment-logs.txt` file.

---

## ✨ What Was Fixed

The latest commit includes:
1. ✅ ConnectionStatus component for diagnostics
2. ✅ Better error logging in API client
3. ✅ Updated docker-compose.prod.yml with hardcoded IP
4. ✅ Environment files for production/development
5. ✅ Debug logging to browser console

---

**Last Updated**: After commit 724b8b2
**GitHub**: https://github.com/MrBadal/Saas_rag
