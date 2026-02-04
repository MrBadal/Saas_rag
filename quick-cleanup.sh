#!/bin/bash
# Quick cleanup without removing running containers
# Safe to run anytime

echo "🧹 Quick Docker Cleanup (Safe Mode)"
echo "===================================="

echo "Removing dangling images..."
docker image prune -f

echo "Removing unused build cache..."
docker builder prune -f

echo "Removing stopped containers..."
docker container prune -f

echo "✅ Quick cleanup done!"
df -h | grep -E "(Filesystem|/dev/)"
