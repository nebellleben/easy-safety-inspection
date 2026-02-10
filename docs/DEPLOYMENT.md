# Deployment Guide

This guide covers deploying the Easy Safety Inspection application to production on Railway.

## Railway Deployment

The application is currently deployed on Railway at:
- Frontend: https://frontend-production-c9d2.up.railway.app
- Backend API: https://safety-backend-production.up.railway.app

### Project Structure on Railway

The project has the following services:
- **frontend**: React web application (served by nginx)
- **safety-backend**: FastAPI backend server
- **bot**: Telegram bot worker
- **Postgres**: PostgreSQL database

### Environment Variables

#### Backend (safety-backend)
| Variable | Value |
|----------|-------|
| PORT | 8000 |
| DATABASE_URL | Railway PostgreSQL connection |
| SECRET_KEY | Auto-generated |
| SERVICE_TYPE | api |

#### Bot Service
| Variable | Value |
|----------|-------|
| SERVICE_TYPE | bot |
| TELEGRAM_BOT_TOKEN | Your bot token from @BotFather |

#### Frontend
| Variable | Value |
|----------|-------|
| PORT | 80 |
| VITE_API_URL | https://safety-backend-production.up.railway.app |

### Deploying to Railway

#### Initial Setup

1. Create a new project on Railway
2. Add a PostgreSQL plugin
3. Link your GitHub repository

#### Service Configuration

**Frontend Service:**
- Dockerfile: `frontend/Dockerfile`
- Port: 80
- Environment: `VITE_API_URL`

**Backend Service:**
- Dockerfile: `backend/Dockerfile`
- Port: 8000
- Uses docker-entrypoint.sh to run API server

**Bot Service:**
- Dockerfile: `backend/Dockerfile`
- Start Command: `python -m app.bot.worker`
- Environment: `SERVICE_TYPE=bot`, `TELEGRAM_BOT_TOKEN`

#### Railway Configuration

The root `railway.toml` configures the PostgreSQL plugin and frontend service:

```toml
# Railway Configuration for Easy Safety Inspection

# PostgreSQL Plugin (shared by all services)
[[plugins]]
plugin = "postgresql"

# Frontend Service
[[services]]
name = "frontend"
dockerfilePath = "frontend/Dockerfile"
[services.env]
PORT = "80"
```

The backend services use their own `railway.toml`:

```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "python -m app.bot.worker"  # For bot service
```

### Deploying Commands

```bash
# Deploy frontend
cd frontend
railway up --service frontend

# Deploy backend
cd backend
railway up --service safety-backend

# Deploy bot
cd backend
railway up --service bot
```

### Database Setup

After deploying the backend for the first time, run the database initialization:

```bash
curl -X POST https://safety-backend-production.up.railway.app/api/v1/setup/initialize
```

This creates:
- Super admin user (ADMIN001 / admin123)
- Default areas (Workshop, Equipment Room, Storage Room, Trackside, Office, Others)

## Default Admin Credentials

- **Staff ID**: `ADMIN001`
- **Password**: `admin123`

⚠️ **Important**: Change the default password after first login!

## Updating Departments and Areas

### Departments
Located in `backend/app/bot/handlers/register.py`:

```python
DEPARTMENTS = [
    "IMD",
    "RSMD",
    "FMD",
    "Others",
]
```

### Areas
Areas are stored in the database. To update them, use the Areas management page in the web interface or update via database migration.

## Monitoring

### Health Checks

- Backend: `https://safety-backend-production.up.railway.app/health`
- Response: `{"status": "ok", "app": "Easy Safety Inspection", "version": "0.1.0"}`

### Logs

View logs using Railway CLI:
```bash
# All services
railway logs

# Specific service
railway logs --service frontend
railway logs --service safety-backend
railway logs --service bot
```

### Service Status

```bash
railway status
```

## Troubleshooting

### Frontend shows "Application failed to respond"

The frontend might be running the wrong code. Redeploy from the frontend directory:
```bash
cd frontend
railway link --service frontend
railway up
```

### Bot is not responding

1. Check bot logs: `railway logs --service bot`
2. Verify TELEGRAM_BOT_TOKEN is complete (not truncated)
3. Ensure SERVICE_TYPE=bot is set

### Services getting mixed up

The Railway service linkage can get confused. Always deploy from the correct directory:
- Frontend: Deploy from `frontend/` directory
- Backend: Deploy from `backend/` directory
- Bot: Deploy from `backend/` directory

## Security Checklist

- [x] Strong SECRET_KEY generated
- [x] HTTPS enabled (Railway default)
- [ ] Change default admin password
- [ ] Set up regular database backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated

## Backup Strategy

### Database Backup

Railway provides automatic backups for PostgreSQL. Access them via the Railway dashboard.

### Export Data

Use the API to export findings:
```bash
curl -X POST https://safety-backend-production.up.railway.app/api/v1/findings/export \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o findings.xlsx
```
