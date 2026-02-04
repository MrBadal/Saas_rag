#!/bin/bash
# COMPLETE RESET - Nuclear option
# WARNING: This will delete EVERYTHING and start fresh

echo "☢️  COMPLETE RESET - Starting Fresh"
echo "===================================="
echo "⚠️  This will delete all containers, images, and the project directory"
echo ""

# Confirm
read -p "Are you sure? Type 'yes' to continue: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "🛑 Step 1: Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || true

echo ""
echo "🗑️  Step 2: Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

echo ""
echo "🗑️  Step 3: Removing all images..."
docker rmi $(docker images -q) 2>/dev/null || true

echo ""
echo "🗑️  Step 4: Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || true

echo ""
echo "🗑️  Step 5: Complete Docker cleanup..."
docker system prune -af --volumes

echo ""
echo "🗑️  Step 6: Clearing build cache..."
docker builder prune -af

echo ""
echo "📁 Step 7: Removing project directory..."
cd ~
rm -rf SaaS_rag

echo ""
echo "📥 Step 8: Cloning fresh from GitHub..."
git clone https://github.com/MrBadal/Saas_rag.git

echo ""
echo "📂 Step 9: Entering project directory..."
cd SaaS_rag

echo ""
echo "🔧 Step 10: Setting up scripts..."
chmod +x *.sh

echo ""
echo "✅ RESET COMPLETE!"
echo ""
echo "📊 Current disk usage:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""
echo "🚀 Next step: Deploy the application"
echo "   Run: ./deploy-with-cleanup.sh"
