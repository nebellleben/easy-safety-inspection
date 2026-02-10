# Deployment Guide

This guide covers deploying the Easy Safety Inspection application to production.

## Prerequisites

- A server with Docker and Docker Compose installed
- A domain name (optional, for HTTPS)
- A Telegram Bot Token
- Production database (PostgreSQL)
- S3-compatible storage (AWS S3, MinIO, etc.)

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Application
APP_NAME=Easy Safety Inspection
APP_VERSION=0.1.0
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_ECHO=false

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# S3 Storage
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=safety-inspection
S3_REGION=us-east-1
S3_USE_SSL=true

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# Frontend
FRONTEND_URL=https://your-domain.com

# CORS
CORS_ORIGINS=https://your-domain.com

# Notifications
DAILY_SUMMARY_TIME=09:00
WEEKLY_SUMMARY_DAY=0
```

## Production Docker Compose

Create a `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  backend:
    image: safety-inspection-backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - S3_ENDPOINT_URL=${S3_ENDPOINT_URL}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    ports:
      - "8000:8000"
    restart: unless-stopped

  bot:
    image: safety-inspection-backend:latest
    command: python -m app.bot.worker
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped

  frontend:
    image: safety-inspection-frontend:latest
    ports:
      - "80:80"
    restart: unless-stopped
```

## Building Images

### Backend
```bash
cd backend
docker build -t safety-inspection-backend:latest .
```

### Frontend
For production, build a static deployment:

```bash
cd frontend
npm run build
# Use nginx:alpine for serving static files
```

## Database Migrations

Run migrations on the production database:

```bash
docker-compose exec backend alembic upgrade head
```

Or using the migration container:

```bash
docker run --rm \
  -e DATABASE_URL=$DATABASE_URL \
  safety-inspection-backend:latest \
  alembic upgrade head
```

## Creating the Super Admin

Create the initial super admin user:

```bash
docker-compose exec backend python -c "
from app.db.session import async_session
from app.repositories.user import UserRepository
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with async_session() as db:
        repo = UserRepository(db)
        user = await repo.create({
            'full_name': 'Super Admin',
            'staff_id': 'ADMIN001',
            'department': 'Administration',
            'section': 'IT',
            'role': 'super_admin',
            'password_hash': get_password_hash('secure-password'),
            'is_active': True,
        })
        await db.commit()
        print(f'Admin created: {user.staff_id}')

asyncio.run(create_admin())
"
```

## Setting Up Telegram Webhook

For production, set up a webhook instead of polling:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/webhook"
```

## SSL/HTTPS Configuration

### Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Frontend
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Bot Webhook
    location /webhook {
        proxy_pass http://bot:8080;
    }
}
```

### Using Caddy (Automatic HTTPS)

```
your-domain.com {
    reverse_proxy /api* backend:8000
    reverse_proxy /webhook bot:8080
    root * /var/www/frontend/dist
    try_files {path} /index.html
}
```

## Monitoring

### Health Checks

- Backend: `http://your-domain.com:8000/health`
- Response: `{"status": "ok", "app": "Easy Safety Inspection", "version": "0.1.0"}`

### Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f bot
```

## Backup Strategy

### Database Backup

```bash
# Daily backup cron job
0 2 * * * docker-compose exec -T postgres pg_dump -U postgres safety_inspection > /backups/db_$(date +\%Y\%m\%d).sql
```

### S3 Backup

For MinIO, use `mc` (MinIO Client):
```bash
mc mirror minio/safety-inspection /backups/s3-$(date +%Y%m%d)
```

## Scaling Considerations

### Horizontal Scaling

- Run multiple backend instances behind a load balancer
- Use external PostgreSQL (RDS, Cloud SQL, etc.)
- Use Redis for session management

### Bot Worker Scaling

For high-volume deployments, run multiple bot workers:
```yaml
bot:
  image: safety-inspection-backend:latest
  deploy:
    replicas: 3
```

## Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled
- [ ] Firewall rules configured
- [ ] Database access restricted
- [ ] S3 bucket permissions set correctly
- [ ] Regular security updates applied
- [ ] Log aggregation set up
- [ ] Monitoring/alerting configured
