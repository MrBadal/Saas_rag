#!/bin/bash
# Deploy with automatic disk cleanup
# This script cleans up Docker before building to prevent "no space left on device" errors

set -e  # Exit on error

echo "🚀 Starting deployment with automatic cleanup..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Show current disk usage
echo ""
echo "📊 Current Disk Usage:"
df -h | grep -E "(Filesystem|/dev/)"

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    print_warning "Disk usage is at ${DISK_USAGE}%. Cleaning up before deployment..."
    CLEANUP_NEEDED=true
else
    print_status "Disk usage is at ${DISK_USAGE}%. Good to proceed."
    CLEANUP_NEEDED=false
fi

# Step 1: Quick cleanup (safe)
echo ""
print_status "Step 1: Running quick cleanup..."
docker system prune -f || true

# Step 2: If disk is still full, aggressive cleanup
if [ "$CLEANUP_NEEDED" = true ] || [ "$DISK_USAGE" -gt 90 ]; then
    echo ""
    print_warning "Step 2: Disk still nearly full. Running aggressive cleanup..."
    
    # Stop all containers
    print_status "Stopping all containers..."
    docker stop $(docker ps -aq) 2>/dev/null || true
    
    # Remove all containers
    print_status "Removing all containers..."
    docker rm $(docker ps -aq) 2>/dev/null || true
    
    # Remove all unused images
    print_status "Removing unused images..."
    docker image prune -af
    
    # Remove all unused volumes (careful with this!)
    print_status "Removing unused volumes..."
    docker volume prune -f
    
    # Full system cleanup
    print_status "Full system cleanup..."
    docker system prune -af --volumes
    
    # Clear build cache
    print_status "Clearing build cache..."
    docker builder prune -af
fi

# Show disk usage after cleanup
echo ""
echo "📊 Disk Usage After Cleanup:"
df -h | grep -E "(Filesystem|/dev/)"

# Check if we have enough space now
DISK_USAGE_AFTER=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE_AFTER" -gt 95 ]; then
    print_error "CRITICAL: Disk is still ${DISK_USAGE_AFTER}% full!"
    print_error "You need to manually free up space or expand the disk."
    print_error "Try: sudo apt-get clean && sudo rm -rf /tmp/*"
    exit 1
fi

# Step 3: Pull latest code
echo ""
print_status "Step 3: Pulling latest code..."
git pull origin main

# Step 4: Build and deploy
echo ""
print_status "Step 4: Building and deploying..."

# Build with no-cache to ensure clean build
# Use COMPOSE_PARALLEL_LIMIT to reduce resource usage
docker-compose -f docker-compose.prod.yml build --no-cache --parallel 1

# Start services
echo ""
print_status "Step 5: Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo ""
print_status "Step 6: Waiting for services to start..."
sleep 10

# Check service status
echo ""
print_status "Step 7: Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Test backend health
echo ""
print_status "Step 8: Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend is healthy!"
else
    print_error "Backend health check failed!"
    print_warning "Check logs with: docker-compose -f docker-compose.prod.yml logs backend"
fi

# Final cleanup after successful deployment
echo ""
print_status "Step 9: Final cleanup..."
docker system prune -f

# Show final status
echo ""
echo "================================================"
print_status "Deployment Complete!"
echo ""
echo "📊 Final Disk Usage:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""
echo "🌐 Access your application at:"
echo "   Frontend: http://13.233.168.67"
echo "   Backend:  http://13.233.168.67:8000"
echo ""
echo "💡 Useful commands:"
echo "   View logs:  docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop all:   docker-compose -f docker-compose.prod.yml down"
echo "   Restart:    docker-compose -f docker-compose.prod.yml restart"
