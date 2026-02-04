#!/bin/bash
# Fix and restart backend service

echo "🔧 Fixing Backend Connection Issue"
echo "==================================="

# Check if containers are running
echo "📋 Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Check if backend is running
echo ""
echo "🔍 Checking if backend is responding..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running locally"
else
    echo "❌ Backend is not running"
fi

# Test external access
echo ""
echo "🌐 Testing external access..."
if curl -s http://13.233.168.67:8000/health > /dev/null; then
    echo "✅ Backend accessible externally"
else
    echo "❌ Backend not accessible externally (Security Group issue?)"
fi

# Check backend logs
echo ""
echo "📜 Backend logs (last 50 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=50 backend

# Check if port 8000 is listening
echo ""
echo "🔌 Checking if port 8000 is open..."
sudo netstat -tlnp | grep 8000 || sudo ss -tlnp | grep 8000 || echo "Port 8000 not found"

# Restart if needed
echo ""
echo "🔄 Would you like to restart the backend? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Restarting backend..."
    docker-compose -f docker-compose.prod.yml restart backend
    sleep 5
    echo ""
    echo "Checking status after restart..."
    docker-compose -f docker-compose.prod.yml ps
fi
