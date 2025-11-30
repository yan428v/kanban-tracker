# Auth Service

Authentication and user management microservice for Kanban Tracker.

## Features

- User registration
- User authentication (JWT-based)
- Password management
- Token refresh

## Technology Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database (via asyncpg)
- **python-jose** - JWT handling
- **passlib + bcrypt** - Password hashing

## Setup

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run migrations
alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload --port 8001
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/auth_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Authenticate user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/change-password` - Change user password

API documentation available at: `http://localhost:8001/docs`

## Development

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src

# Generate migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```
