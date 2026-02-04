#!/bin/bash
# Setup script for fresh AWS deployment
# Run this if the project doesn't exist on the server

echo "🚀 Setting up Universal RAG on AWS"
echo "===================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone the repository
echo "📥 Cloning repository..."
cd ~
git clone https://github.com/MrBadal/Saas_rag.git
cd SaaS_rag

# Show current directory
echo ""
echo "✅ Setup complete!"
echo "📁 Project location: $(pwd)"
echo ""
echo "Next steps:"
echo "1. Check disk space: df -h"
echo "2. Run cleanup: ./cleanup-docker.sh"
echo "3. Deploy: ./deploy-with-cleanup.sh"
