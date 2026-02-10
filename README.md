# Easy Safety Inspection

A safety inspection finding management system that allows users to report safety issues via Telegram bot, with a web admin interface for managing findings, tracking progress, and generating reports.

## Features

- **Telegram Bot Reporting**: Users can easily report safety findings with photos and descriptions
- **User Registration**: Simple registration flow via Telegram bot
- **Role-Based Access Control**: Reporter, Admin, and Super-Admin roles
- **Area-Based Management**: Hierarchical area structure (2-3 levels)
- **Severity Levels**: Low, Medium, High, Critical
- **Status Tracking**: Open, In Progress, Resolved, Closed
- **Notifications**: Real-time alerts and periodic summaries
- **Web Admin Interface**: Dashboard, findings management, reports

## Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL
- **Storage**: S3-compatible (MinIO for local)
- **Bot Framework**: python-telegram-bot
- **Task Queue**: APScheduler (for scheduled summaries)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd easy-safety-inspection
```

2. Copy environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` and add your Telegram bot token:
```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
```

3. Start all services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

5. Create a super-admin user (optional, for development):
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
            'password_hash': get_password_hash('admin123'),
            'is_active': True,
        })
        await db.commit()
        print(f'Admin user created: {user.staff_id}')

asyncio.run(create_admin())
"
```

### Access the Application

- **Web Interface**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

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
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   ├── styles/         # CSS files
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── docs/                   # Documentation
├── docker-compose.yml      # Local development
└── README.md
```

## Usage

### For Reporters (Telegram Bot)

1. Open Telegram and search for your bot
2. Send `/start` to begin
3. Send `/register` to register your account
4. Send `/report` to submit a safety finding

### For Admins (Web Interface)

1. Login with your staff ID and password
2. View findings on the Dashboard
3. Filter and manage findings in the Findings page
4. Generate reports in the Reports page
5. Configure notifications in Settings

### For Super-Admins

- Manage users in Admin → Users
- Manage areas in Admin → Areas
- Assign admins to specific areas

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm run test
```

## License

MIT License

## Support

For support and questions, please open an issue on GitHub.
