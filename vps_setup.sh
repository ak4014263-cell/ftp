#!/bin/bash

# VPS Initial Setup Script for Swiply
# Run this once on a fresh VPS to install all dependencies

set -e

echo "🚀 Swiply VPS Setup Script"
echo "==========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}" 
   echo "Please run: sudo bash vps_setup.sh"
   exit 1
fi

echo -e "${BLUE}📦 Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo ""
echo -e "${BLUE}🐳 Installing Docker...${NC}"

# Remove old Docker versions
apt-get remove -y docker docker-engine docker.io containerd runc || true

# Install dependencies
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
systemctl start docker
systemctl enable docker

echo -e "${GREEN}✅ Docker installed${NC}"

echo ""
echo -e "${BLUE}🐙 Installing Docker Compose...${NC}"

# Install Docker Compose v2
apt-get install -y docker-compose-plugin

# Also install standalone docker-compose for compatibility
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo -e "${GREEN}✅ Docker Compose installed${NC}"
docker-compose --version

echo ""
echo -e "${BLUE}🐍 Installing Python and utilities...${NC}"

apt-get install -y \
    python3 \
    python3-pip \
    git \
    htop \
    vim \
    nano \
    wget \
    curl \
    unzip \
    openssl \
    net-tools \
    build-essential

echo -e "${GREEN}✅ Python and utilities installed${NC}"

echo ""
echo -e "${BLUE}🔥 Installing fail2ban (security)...${NC}"

apt-get install -y fail2ban

# Configure fail2ban
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
EOF

systemctl enable fail2ban
systemctl start fail2ban

echo -e "${GREEN}✅ fail2ban installed and configured${NC}"

echo ""
echo -e "${BLUE}🔒 Configuring firewall...${NC}"

# Install ufw
apt-get install -y ufw

# Allow SSH (IMPORTANT!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
echo "y" | ufw enable

echo -e "${GREEN}✅ Firewall configured${NC}"

echo ""
echo -e "${BLUE}⚙️  Optimizing for browser automation...${NC}"

# Increase shared memory (needed for browser)
echo "tmpfs /dev/shm tmpfs defaults,size=2g 0 0" >> /etc/fstab
mount -o remount /dev/shm

# Increase file descriptors
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65536
* hard nofile 65536
EOF

echo -e "${GREEN}✅ System optimized${NC}"

echo ""
echo -e "${BLUE}📁 Creating application directory...${NC}"

APP_DIR="/opt/swiply"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${GREEN}✅ Created directory: $APP_DIR${NC}"

echo ""
echo -e "${BLUE}🔑 Setting up non-root user...${NC}"

# Create swiply user if doesn't exist
if ! id "swiply" &>/dev/null; then
    useradd -m -s /bin/bash swiply
    usermod -aG docker swiply
    echo -e "${GREEN}✅ Created user: swiply${NC}"
else
    echo -e "${YELLOW}⚠️  User swiply already exists${NC}"
fi

# Give swiply ownership of app directory
chown -R swiply:swiply $APP_DIR

echo ""
echo "=================================="
echo -e "${GREEN}✅ VPS Setup Complete!${NC}"
echo "=================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Switch to swiply user:"
echo -e "   ${YELLOW}su - swiply${NC}"
echo ""
echo "2. Clone your repository:"
echo -e "   ${YELLOW}cd /opt/swiply${NC}"
echo -e "   ${YELLOW}git clone https://github.com/yourusername/yourrepo.git .${NC}"
echo ""
echo "3. Create .env.production file:"
echo -e "   ${YELLOW}cp .env.production.example .env.production${NC}"
echo -e "   ${YELLOW}nano .env.production${NC}"
echo ""
echo "   ⚠️  IMPORTANT: Add your proxy credentials!"
echo ""
echo "4. Deploy the application:"
echo -e "   ${YELLOW}bash deploy.sh${NC}"
echo ""
echo "5. Monitor IP health:"
echo -e "   ${YELLOW}python3 monitor_ip_health.py${NC}"
echo ""
echo "=================================="
echo ""
echo "🔒 Security Notes:"
echo "  - SSH is allowed on port 22 (change this in production!)"
echo "  - HTTP (80) and HTTPS (443) are open"
echo "  - fail2ban is active to prevent brute force attacks"
echo "  - Firewall (ufw) is enabled"
echo ""
echo "📊 Useful commands:"
echo "  - View firewall status: sudo ufw status"
echo "  - View Docker containers: docker ps"
echo "  - View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.production.yml down"
echo ""
echo -e "${GREEN}🎉 Your VPS is ready for Swiply deployment!${NC}"
echo ""
