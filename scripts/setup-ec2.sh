#!/bin/bash

# Initial setup script for EC2 instance
# Run this once when setting up the EC2 instance for the first time

set -e

echo "=========================================="
echo "EC2 Instance Setup for SaaS RAG"
echo "=========================================="

# Update system
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "[2/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "[3/8] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed"
fi

# Install Git
echo "[4/8] Installing Git..."
sudo apt install -y git

# Install other useful tools
echo "[5/8] Installing additional tools..."
sudo apt install -y curl htop nginx

# Create app directory
echo "[6/8] Creating application directory..."
mkdir -p ~/SaaS_rag

# Setup swap space (important for t2.micro with 1GB RAM)
echo "[7/8] Setting up swap space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap space created (2GB)"
else
    echo "Swap space already exists"
fi

# Configure sysctl for better memory management
echo "[8/8] Configuring system settings..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

echo ""
echo "=========================================="
echo "EC2 Setup Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT NEXT STEPS:"
echo ""
echo "1. Logout and login again for Docker group changes to take effect:"
echo "   exit"
echo "   # Then SSH back in"
echo ""
echo "2. Clone your repository:"
echo "   git clone <your-github-repo-url> ~/SaaS_rag"
echo ""
echo "3. Add your EC2 SSH key to GitHub Secrets for CI/CD:"
echo "   cat ~/.ssh/authorized_keys"
echo "   # Copy this key and add it as EC2_SSH_KEY in GitHub Secrets"
echo ""
echo "4. Get your EC2 instance metadata:"
echo "   Public IP: curl http://169.254.169.254/latest/meta-data/public-ipv4"
echo "   Instance ID: curl http://169.254.169.254/latest/meta-data/instance-id"
echo ""
echo "5. After cloning, run the deployment script manually first time:"
echo "   cd ~/SaaS_rag"
echo "   ./scripts/deploy.sh"
echo ""
echo "=========================================="