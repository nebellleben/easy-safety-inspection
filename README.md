# Easy Safety Inspection

A safety inspection finding management system that allows users to report safety issues via Telegram bot, with a web admin interface for managing findings, tracking progress, and generating reports.

## Features

- **Telegram Bot Reporting**: Users can easily report safety findings with photos and descriptions
- **User Registration**: Simple registration flow via Telegram bot
- **Role-Based Access Control**: Reporter, Admin, and Super-Admin roles
- **Area-Based Management**: Predefined areas for categorizing findings
- **Severity Levels**: Low, Medium, High, Critical
- **Status Tracking**: Open, In Progress, Resolved, Closed
- **Notifications**: Real-time alerts and periodic summaries
- **Web Admin Interface**: Dashboard, findings management, reports

## Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL
- **Bot Framework**: python-telegram-bot
- **Deployment**: Railway (cloud platform)

## Production Deployment

**Services**:
- Frontend: https://frontend-production-c9d2.up.railway.app
- Backend API: https://safety-backend-production.up.railway.app
- Telegram Bot: Running on Railway

**Default Admin Credentials**:
- Staff ID: `ADMIN001`
- Password: `admin123`

## Quick Start (Local Development)

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd easy-safety-inspection
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- **Web Interface**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
easy-safety-inspection/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── bot/            # Telegram bot handlers
│   │   ├── core/           # Security, config, dependencies
│   │   ├── db/             # Database session
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Database repositories
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docs/                   # Documentation
└── railway.toml            # Railway deployment config
```

## Configuration

### Departments

Users can register with one of these departments:
- IMD
- RSMD
- FMD
- Others

### Areas for Reporting

Findings can be reported in these areas:
- Workshop
- Equipment Room
- Storage Room
- Trackside
- Office
- Others

### Severity Levels

- 🟢 **Low** - Minor issue, no immediate risk
- 🟡 **Medium** - Needs attention soon
- 🟠 **High** - Significant safety concern
- 🔴 **Critical** - Immediate danger, urgent action required

## Usage

### For Reporters (Telegram Bot)

1. Open Telegram and search for your bot
2. Send `/start` to begin
3. Send `/register` to register your account
4. Send `/report` to submit a safety finding with photo

**Registration Flow:**
1. Enter your full name
2. Enter your Staff ID
3. Select your department (IMD, RSMD, FMD, Others)
4. Enter your section (e.g., KBD, EAL, Civil, L&AV...)
5. Confirm your details

**Reporting Flow:**
1. Select the area where the issue was found
2. Describe the safety issue
3. Upload a photo (or type "skip" to continue without)
4. Select the severity level
5. Enter the specific location (optional)

### For Admins (Web Interface)

1. Login with your staff ID and password
2. View findings on the Dashboard
3. Filter and manage findings in the Findings page
4. Generate reports in the Reports page

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## License

MIT License
