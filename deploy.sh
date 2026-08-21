#!/bin/bash

set -e  # Exit on error

echo "=================================================="
echo "🚀 Swiply VPS Production Deployment Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}⚠️  .env.production not found. Creating from .env.production.example...${NC}"
    if [ -f .env.production.example ]; then
        cp .env.production.example .env.production
        echo -e "${GREEN}✅ Created .env.production${NC}"
    else
        echo -e "${RED}❌ Error: .env.production.example not found!${NC}"
        exit 1
    fi
fi

# Load environment variables
echo "📋 Loading environment variables..."
set -a
source .env.production
set +a

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p screenshots/apply_debug
mkdir -p firefox_profile
mkdir -p browser_sessions
mkdir -p ssl
mkdir -p logs
mkdir -p certbot/conf
mkdir -p certbot/www

# Generate self-signed SSL certificate fallback if missing (ensures Nginx starts cleanly)
if [ ! -f ssl/fullchain.pem ] || [ ! -f ssl/privkey.pem ]; then
    echo -e "${BLUE}🔐 Generating self-signed SSL certificate for initial launch...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/privkey.pem -out ssl/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=Swiply/CN=localhost" > /dev/null 2>&1 || true
    echo -e "${GREEN}✅ Initial SSL certificates ready in ./ssl${NC}"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.production.yml down || docker-compose -f docker-compose.production.yml down || true

# Build images
echo "🏗️  Building Docker images with Firefox automation support..."
docker compose -f docker-compose.production.yml build || docker-compose -f docker-compose.production.yml build

# Start services
echo "🎬 Starting all microservices..."
docker compose -f docker-compose.production.yml up -d || docker-compose -f docker-compose.production.yml up -d

# Wait for services to initialize
echo "⏳ Waiting for services to initialize (25 seconds)..."
sleep 25

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker compose -f docker-compose.production.yml ps || docker-compose -f docker-compose.production.yml ps

# Test Postgres connection
echo ""
echo "🔍 Testing database connection..."
if docker exec swiply-postgres pg_isready -U "${POSTGRES_USER:-swiply}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Database is still initializing...${NC}"
fi

# Test Redis connection
echo "🔍 Testing Redis connection..."
if docker exec swiply-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Redis is still initializing...${NC}"
fi

# Test API Gateway health
echo "🔍 Testing API Gateway health..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API Gateway is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  API Gateway starting up (check: docker logs swiply-gateway)${NC}"
fi

# Final status
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 All Swiply Services Deployed Successfully!${NC}"
echo "=================================================="
echo ""
echo "🌐 Access Endpoints:"
echo "   - Web App / Dashboard:  http://<YOUR_VPS_IP>/"
echo "   - API Gateway:          http://<YOUR_VPS_IP>:8000"
echo "   - Gateway Health:       http://<YOUR_VPS_IP>:8000/health"
echo "   - WTTJ Firefox Auto:    http://<YOUR_VPS_IP>:8012"
echo ""
echo "📊 Useful Management Commands:"
echo "   - View all logs:        docker compose -f docker-compose.production.yml logs -f"
echo "   - View Firefox logs:    docker logs -f swiply-wttj"
echo "   - Restart all:          docker compose -f docker-compose.production.yml restart"
echo "   - Stop all:             docker compose -f docker-compose.production.yml down"
echo "=================================================="
