#!/bin/bash
# Emergency Disk Cleanup Script for Docker/AWS
# Run this when you get "no space left on device" errors

echo "🚨 EMERGENCY DISK CLEANUP 🚨"
echo "=============================="

# Show current disk usage
echo ""
echo "📊 Current Disk Usage:"
df -h

echo ""
echo "🐳 Docker Disk Usage:"
docker system df

echo ""
echo "🧹 Step 1: Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers running"

echo ""
echo "🧹 Step 2: Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

echo ""
echo "🧹 Step 3: Removing unused images..."
docker image prune -af

echo ""
echo "🧹 Step 4: Removing unused volumes..."
docker volume prune -f

echo ""
echo "🧹 Step 5: Removing unused networks..."
docker network prune -f

echo ""
echo "🧹 Step 6: Complete system cleanup..."
docker system prune -af --volumes

echo ""
echo "🧹 Step 7: Clearing build cache..."
docker builder prune -af

echo ""
echo "📊 Disk Usage After Cleanup:"
df -h

echo ""
echo "🐳 Docker Usage After Cleanup:"
docker system df

echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "💡 Tip: To prevent this in the future, run this script weekly or set up a cron job:"
echo "   0 2 * * 0 /path/to/cleanup-docker.sh"
