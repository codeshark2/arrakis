# Deployment Guide

This guide covers deploying Arrakis to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Environment Configuration](#environment-configuration)
- [Production Best Practices](#production-best-practices)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Server**: Linux server (Ubuntu 20.04+ recommended)
- **Docker**: Docker 20.10+ and Docker Compose 2.0+
- **Supabase Account**: For database and authentication
- **Perplexity AI API Key**: For AI-powered analysis
- **Domain Name**: For production deployment (optional for testing)

### Recommended

- **Nginx**: For reverse proxy and SSL termination
- **SSL Certificate**: Let's Encrypt or commercial certificate
- **Monitoring**: Prometheus, Grafana, or similar
- **Logging**: ELK stack or similar

---

## Docker Deployment (Recommended)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/codeshark2/arrakis.git
cd arrakis

# 2. Create environment files
cp backend/env.sample backend/.env
cp frontend/env.local.sample frontend/.env.local

# 3. Edit environment files with your production values
nano backend/.env
nano frontend/.env.local

# 4. Start the application
docker-compose up -d

# 5. Verify services are running
docker-compose ps
docker-compose logs -f
```

### Docker Compose Configuration

For production, create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: arrakis-backend
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - arrakis-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    container_name: arrakis-frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - arrakis-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: arrakis-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - arrakis-network

networks:
  arrakis-network:
    driver: bridge

volumes:
  nginx-logs:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Manual Deployment

### Backend Deployment

```bash
# 1. Set up Python environment
cd backend
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp env.sample .env
nano .env

# 4. Run with Gunicorn (production WSGI server)
pip install gunicorn uvicorn[standard]
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend Deployment

```bash
# 1. Install dependencies
cd frontend
npm ci --production

# 2. Configure environment
cp env.local.sample .env.local
nano .env.local

# 3. Build for production
npm run build

# 4. Start production server
npm start
```

### Systemd Service Setup

Create `/etc/systemd/system/arrakis-backend.service`:

```ini
[Unit]
Description=Arrakis Backend API
After=network.target

[Service]
Type=simple
User=arrakis
WorkingDirectory=/opt/arrakis/backend
Environment="PATH=/opt/arrakis/backend/venv/bin"
ExecStart=/opt/arrakis/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/arrakis-frontend.service`:

```ini
[Unit]
Description=Arrakis Frontend
After=network.target

[Service]
Type=simple
User=arrakis
WorkingDirectory=/opt/arrakis/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable arrakis-backend arrakis-frontend
sudo systemctl start arrakis-backend arrakis-frontend
sudo systemctl status arrakis-backend arrakis-frontend
```

---

## Nginx Configuration

Create `/etc/nginx/sites-available/arrakis`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for Next.js HMR in dev)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files caching
    location /_next/static {
        proxy_pass http://frontend;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/arrakis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Environment Configuration

### Backend (.env)

```bash
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Perplexity AI (Required)
PERPLEXITY_API_KEY=your-perplexity-api-key

# OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key

# Application
APP_NAME=Arrakis MVP
DEBUG=false
ENVIRONMENT=production

# CORS - Add your frontend domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Frontend (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Optional settings
NEXT_PUBLIC_USE_LOCALSTORAGE=false
NEXT_PUBLIC_API_TIMEOUT=30000
```

---

## Production Best Practices

### Security

1. **Use Environment Variables**: Never commit secrets
2. **Enable HTTPS**: Use Let's Encrypt or commercial SSL
3. **Rate Limiting**: Configure Nginx rate limiting
4. **Firewall**: Configure UFW or iptables
5. **Regular Updates**: Keep dependencies updated
6. **Security Scanning**: Run regular security audits

### Performance

1. **Caching**: Enable Redis for session/cache storage
2. **CDN**: Use CloudFlare or similar for static assets
3. **Database**: Optimize Supabase queries and indexes
4. **Monitoring**: Set up Prometheus/Grafana
5. **Load Balancing**: Use multiple instances behind load balancer

### Reliability

1. **Backups**: Regular database backups
2. **Health Checks**: Configure health check endpoints
3. **Auto-restart**: Use systemd or Docker restart policies
4. **Logging**: Centralized logging with ELK stack
5. **Alerting**: Set up alerts for errors and downtime

---

## Monitoring and Logging

### Health Check Endpoint

```bash
curl http://localhost:8000/api/healthz
```

### View Logs

**Docker:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Systemd:**
```bash
sudo journalctl -u arrakis-backend -f
sudo journalctl -u arrakis-frontend -f
```

### Monitoring Stack

Install Prometheus and Grafana:
```bash
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3001:3000 grafana/grafana
```

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep SUPABASE

# Test database connection
docker-compose exec backend python -c "from app.supabase.client import db; print('OK')"
```

### Frontend build fails

```bash
# Clear Next.js cache
rm -rf frontend/.next
rm -rf frontend/node_modules
npm ci
npm run build
```

### SSL Certificate Issues

```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Test certificate
sudo certbot certificates
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check database performance
# Review Supabase dashboard

# Enable profiling
# Add --profile flag to Gunicorn
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Add nginx or HAProxy
2. **Multiple Instances**: Run multiple backend containers
3. **Session Storage**: Use Redis for shared sessions
4. **Database**: Use Supabase connection pooling

### Vertical Scaling

1. **Increase Resources**: More CPU/RAM for containers
2. **Worker Processes**: Increase Gunicorn workers
3. **Database**: Upgrade Supabase tier

---

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build
docker-compose up -d

# Or for manual deployment
pip install -r requirements.txt --upgrade
npm ci
npm run build
sudo systemctl restart arrakis-backend arrakis-frontend
```

### Backups

```bash
# Backup database (handled by Supabase)
# Backup environment files
tar -czf arrakis-config-$(date +%Y%m%d).tar.gz backend/.env frontend/.env.local

# Backup custom code/configs
tar -czf arrakis-backup-$(date +%Y%m%d).tar.gz --exclude=node_modules --exclude=venv .
```

---

## Support

For deployment issues:
- Check [GitHub Issues](https://github.com/codeshark2/arrakis/issues)
- Review [API Documentation](API.md)
- Join [GitHub Discussions](https://github.com/codeshark2/arrakis/discussions)
