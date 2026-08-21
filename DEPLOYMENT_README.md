# Swiply VPS Deployment Guide

## 🚨 Problem: IP Getting Blocked on VPS

When you run browser automation on a VPS without proper precautions, your IP gets blocked because:

1. **VPS IPs are datacenter IPs** - Anti-bot systems flag these immediately
2. **No browsing history** - Fresh browsers look suspicious
3. **Predictable patterns** - No human-like delays or behavior
4. **High frequency** - Too many requests too quickly
5. **No residential IP reputation** - Looks like a bot farm

## ✅ Solution Overview

This deployment guide implements **5 anti-blocking layers**:

1. **Residential Proxy Rotation** - Distribute requests across real user IPs
2. **Rate Limiting** - Stay under detection thresholds  
3. **Session Persistence** - Look like returning users
4. **Stealth Browser** - Hide automation fingerprints
5. **Request Monitoring** - Detect and respond to blocks early

---

## 📋 Prerequisites

### 1. VPS Server

**Recommended providers** (good IP reputation):
- **Hetzner** - €5-40/month, European datacenters
- **DigitalOcean** - $6-48/month, global datacenters
- **Linode** - $5-40/month, reliable network

**Minimum specs:**
- 2 CPU cores
- 4 GB RAM (8 GB recommended for browser automation)
- 50 GB SSD storage
- Ubuntu 20.04 or 22.04 LTS

**❌ Avoid:**
- AWS EC2 (flagged datacenter IPs)
- GCP Compute (same issue)
- Very cheap providers (IPs usually banned)

### 2. Proxy Service (CRITICAL!)

**You MUST use residential proxies on VPS. Options:**

#### Option A: Bright Data (Recommended)
- **Website:** https://brightdata.com
- **Cost:** $50-150/month (starter plan)
- **Features:** Best IP pool, reliable, good support
- **Free trial:** 7 days

#### Option B: Smartproxy
- **Website:** https://smartproxy.com
- **Cost:** $50-100/month
- **Features:** Good value, easy setup

#### Option C: Oxylabs
- **Website:** https://oxylabs.io
- **Cost:** $100-300/month
- **Features:** Premium quality, enterprise-grade

**⚠️  Without proxies, your VPS IP WILL be blocked within hours!**

### 3. Domain Name (Optional but Recommended)

- Purchase from Namecheap, GoDaddy, or Cloudflare
- Point A records to your VPS IP
- Enables HTTPS with Let's Encrypt

---

## 🚀 Quick Start (3 Steps)

### Step 1: Initial VPS Setup

SSH into your VPS and run:

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/yourusername/yourrepo/main/vps_setup.sh
sudo bash vps_setup.sh
```

This installs:
- Docker & Docker Compose
- Python 3 and utilities
- Security tools (fail2ban, firewall)
- System optimizations

### Step 2: Clone Repository & Configure

```bash
# Switch to swiply user
su - swiply

# Clone repository
cd /opt/swiply
git clone https://github.com/yourusername/yourrepo.git .

# Create production environment file
cp .env.production.example .env.production

# Edit configuration
nano .env.production
```

**Edit `.env.production`:**

```bash
# Database (change passwords!)
POSTGRES_USER=swiply
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
POSTGRES_DB=swiply

# API Keys
OPENAI_API_KEY=your-openai-key

# Security
ENCRYPTION_KEY=your-32-character-encryption-key-here

# Domain (if you have one)
VITE_API_URL=https://api.yourdomain.com

# CRITICAL: Proxy Configuration
PROXY_ENABLED=true
PROXY_HOST=brd.superproxy.io
PROXY_PORT=22225
PROXY_USERNAME=your-brightdata-username
PROXY_PASSWORD=your-brightdata-password

# Rate Limiting
RATE_LIMIT_PER_HOUR=20

# Session Persistence
SESSION_PERSISTENCE_ENABLED=true
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 3: Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy!
bash deploy.sh
```

The script will:
- ✅ Check proxy configuration
- ✅ Build Docker images
- ✅ Start all services
- ✅ Run health checks
- ✅ Show logs

---

## 📊 Monitoring & Management

### Check Status

```bash
# View all services
docker-compose -f docker-compose.production.yml ps

# View logs (all services)
docker-compose -f docker-compose.production.yml logs -f

# View logs (specific service)
docker logs -f swiply-wttj
docker logs -f swiply-gateway
```

### Monitor IP Health

```bash
# Manual check
python3 monitor_ip_health.py

# Set up automatic monitoring (every 15 minutes)
crontab -e
# Add this line:
*/15 * * * * cd /opt/swiply && python3 monitor_ip_health.py >> logs/ip_health.log 2>&1
```

### View Rate Limiter Stats

```bash
# Check WTTJ service logs for rate limiting
docker logs swiply-wttj 2>&1 | grep -i "rate limit"

# Check current requests per hour
docker logs swiply-wttj 2>&1 | grep -i "requests_last_hour"
```

### Restart Services

```bash
# Restart specific service
docker restart swiply-wttj

# Restart all services
docker-compose -f docker-compose.production.yml restart

# Stop all services
docker-compose -f docker-compose.production.yml down

# Start all services
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔧 Configuration Details

### Rate Limiting Configuration

Edit `.env.production` to adjust:

```bash
# Conservative (safer, slower)
RATE_LIMIT_PER_HOUR=15

# Moderate (recommended)
RATE_LIMIT_PER_HOUR=20

# Aggressive (risky, faster)
RATE_LIMIT_PER_HOUR=30
```

**Recommendation:** Start with 15-20, monitor for blocks, then gradually increase if stable.

### Proxy Configuration

Different proxy providers have different settings:

**Bright Data:**
```bash
PROXY_HOST=brd.superproxy.io
PROXY_PORT=22225
PROXY_USERNAME=brd-customer-<ID>-zone-<ZONE>
PROXY_PASSWORD=your-password
```

**Smartproxy:**
```bash
PROXY_HOST=gate.smartproxy.com
PROXY_PORT=7000
PROXY_USERNAME=your-username
PROXY_PASSWORD=your-password
```

**Oxylabs:**
```bash
PROXY_HOST=pr.oxylabs.io
PROXY_PORT=7777
PROXY_USERNAME=customer-your-id
PROXY_PASSWORD=your-password
```

### Session Persistence

Sessions are stored in `./browser_sessions/` and persist across restarts.

**View sessions:**
```bash
ls -la browser_sessions/
```

**Clean old sessions:**
```bash
# Remove sessions older than 30 days
find browser_sessions/ -type d -mtime +30 -exec rm -rf {} +
```

---

## 🔍 Troubleshooting

### Issue: IP Still Getting Blocked

**Check proxy is working:**
```bash
docker logs swiply-wttj 2>&1 | grep -i proxy
```

**Expected output:**
```
✅ Proxy configured: brd.superproxy.io:22225
✅ Proxy connection successful
```

**If you see errors:**
1. Verify proxy credentials in `.env.production`
2. Check proxy service is active (login to provider dashboard)
3. Test proxy directly:

```bash
curl -x http://username:password@proxy-host:port https://www.welcometothejungle.com
```

### Issue: Rate Limits Too Restrictive

**Symptoms:** Automation is very slow

**Solution:** Increase rate limit gradually

```bash
# Edit .env.production
nano .env.production

# Change RATE_LIMIT_PER_HOUR to higher value
RATE_LIMIT_PER_HOUR=30

# Restart WTTJ service
docker restart swiply-wttj
```

**Monitor for blocks:** If you start getting blocked, reduce the limit again.

### Issue: Services Not Starting

**Check logs:**
```bash
docker-compose -f docker-compose.production.yml logs
```

**Common issues:**

1. **Port already in use:**
   ```bash
   # Find what's using port 8000
   sudo lsof -i :8000
   # Kill the process or change port in docker-compose.production.yml
   ```

2. **Out of memory:**
   ```bash
   # Check memory
   free -h
   # Reduce Docker memory limits in docker-compose.production.yml
   ```

3. **Database connection failed:**
   ```bash
   # Check database is running
   docker exec swiply-postgres pg_isready -U swiply
   ```

### Issue: High Memory Usage

**Check memory:**
```bash
docker stats
```

**Solution:** Reduce resources in `docker-compose.production.yml`:

```yaml
wttj:
  # ... other config ...
  deploy:
    resources:
      limits:
        cpus: '1.0'      # Reduce from 2.0
        memory: 2G        # Reduce from 4G
```

Then restart:
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Issue: SSL/HTTPS Not Working

**If you don't have a domain:**
- Use HTTP only (services work fine without HTTPS)
- Access via IP: `http://your-vps-ip:8000`

**If you have a domain:**

1. Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Get certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

3. Update `nginx.conf` with certificate paths
4. Restart nginx:
```bash
docker restart swiply-nginx
```

---

## 📈 Performance Optimization

### 1. Use API Instead of Browser When Possible

**Fastest approach:**
- Use Algolia API for job search (no browser needed)
- Use TLS bypass for account operations
- Use ATS direct apply when available

See: `find_ats_endpoint.py` and `services/automation/app/wttj_api_client.py`

### 2. Optimize Docker Images

```bash
# Remove old images
docker system prune -a

# Build with cache (faster rebuilds)
docker-compose -f docker-compose.production.yml build
```

### 3. Enable Redis Caching

Redis is already configured, but you can optimize:

```bash
# Connect to Redis
docker exec -it swiply-redis redis-cli

# Check cache stats
INFO stats

# Flush cache if needed (be careful!)
FLUSHDB
```

### 4. Scale Horizontally

For high volume, run multiple instances:

```yaml
# In docker-compose.production.yml
wttj_worker_1:
  # ... same config as wttj ...
  environment:
    - WORKER_ID=1

wttj_worker_2:
  # ... same config as wttj ...
  environment:
    - WORKER_ID=2
```

---

## 💰 Cost Estimate

### Minimum Setup (Small Scale)
- **VPS:** $10-20/month (Hetzner, 2 CPU, 4GB RAM)
- **Proxy:** $50-100/month (Bright Data starter)
- **Domain:** $10/year (optional)
- **Total:** ~$60-120/month

### Production Setup (Medium Scale)
- **VPS:** $40-80/month (3x instances or larger server)
- **Proxy:** $150-300/month (higher volume)
- **Monitoring:** Free (self-hosted)
- **Total:** ~$190-380/month

### Enterprise Setup (High Scale)
- **VPS:** $200-500/month (distributed, load balanced)
- **Proxy:** $500-1000/month (unlimited)
- **Monitoring:** $50/month (external service)
- **Total:** ~$750-1550/month

---

## 🔐 Security Best Practices

### 1. Change Default Passwords

```bash
# Edit .env.production
nano .env.production

# Change ALL default passwords:
POSTGRES_PASSWORD=use-a-strong-unique-password-here
ENCRYPTION_KEY=generate-32-character-random-string
```

### 2. Set Up SSH Key Authentication

```bash
# On your local machine, generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to VPS
ssh-copy-id swiply@your-vps-ip

# On VPS, disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

### 3. Enable Automatic Security Updates

```bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 4. Set Up Backup

```bash
# Create backup script
cat > /opt/swiply/backup.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/swiply/backups"
mkdir -p $BACKUP_DIR

# Backup database
docker exec swiply-postgres pg_dump -U swiply swiply | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup sessions
tar -czf $BACKUP_DIR/sessions_$DATE.tar.gz browser_sessions/

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/swiply/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /opt/swiply/backup.sh >> /opt/swiply/logs/backup.log 2>&1
```

---

## 📚 Additional Resources

### Documentation Files

- `VPS_DEPLOYMENT_GUIDE.md` - Detailed technical guide
- `ANTI_BOT_SOLUTION_GUIDE.md` - Anti-bot strategies
- `ADVANCED_BYPASS_GUIDE.md` - TLS bypass and ATS discovery

### Scripts

- `deploy.sh` - Main deployment script
- `vps_setup.sh` - Initial VPS setup
- `monitor_ip_health.py` - IP health monitoring

### Configuration Files

- `.env.production.example` - Production environment template
- `docker-compose.production.yml` - Production Docker configuration
- `nginx.conf` - Nginx reverse proxy configuration

---

## 🆘 Getting Help

### Check Logs First

```bash
# View all logs
docker-compose -f docker-compose.production.yml logs

# Search for errors
docker-compose -f docker-compose.production.yml logs | grep -i error

# Follow logs in real-time
docker logs -f swiply-wttj
```

### Common Log Locations

- **Application logs:** `docker logs <container-name>`
- **IP health:** `logs/ip_health.log`
- **Nginx:** `docker logs swiply-nginx`
- **System logs:** `/var/log/syslog`

### Report Issues

When reporting issues, include:
1. Error messages from logs
2. Output of `docker ps -a`
3. Output of `docker-compose -f docker-compose.production.yml logs <service>`
4. Your `.env.production` (with passwords removed!)

---

## ✅ Success Metrics

After deployment, you should see:

**IP Health Check:**
```
✅ All 3 URLs are accessible
🟢 No blocking detected
📊 Response times: 0.2-0.5s
```

**Rate Limiter:**
```
📊 Requests last hour: 15/20
🟢 Utilization: 75%
✅ 0 consecutive errors
```

**Services:**
```
swiply-gateway     running (healthy)
swiply-wttj        running (healthy)
swiply-postgres    running (healthy)
swiply-redis       running (healthy)
```

**Expected success rate with proper setup: 95%+**

---

## 🎉 Congratulations!

Your Swiply application is now deployed on VPS with:

✅ Proxy rotation to prevent IP blocking
✅ Rate limiting for human-like behavior
✅ Session persistence for returning user appearance
✅ Monitoring for early block detection
✅ Secure, production-ready configuration

**Next steps:**
1. Monitor `logs/ip_health.log` for a few days
2. Adjust rate limits based on blocking patterns
3. Set up automatic backups
4. Consider adding more workers for scale

Happy automating! 🚀
