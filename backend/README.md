# Scalper Bot - Backend API

FastAPI-based backend for the cryptocurrency scalping bot dashboard.

## Features

- **FastAPI Framework**: Modern, fast, async web framework
- **PostgreSQL Database**: Async SQLAlchemy with PostgreSQL
- **RESTful API**: Complete CRUD operations for bots and activity logs
- **Auto-generated Docs**: Interactive API documentation with Swagger UI
- **CORS Support**: Configured for Next.js frontend integration
- **Type Safety**: Full Pydantic validation for requests and responses

## Tech Stack

- **Python**: 3.11+
- **Framework**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25 (async)
- **Database**: PostgreSQL with asyncpg driver
- **Validation**: Pydantic 2.5.3
- **Server**: Uvicorn (ASGI)
- **Migrations**: Alembic (planned)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── bots.py          # Bot management endpoints
│   │       │   └── logs.py          # Activity log endpoints
│   │       └── router.py            # API router
│   ├── core/
│   │   └── config.py                # Application configuration
│   ├── db/
│   │   └── session.py               # Database session management
│   ├── models/
│   │   └── bot.py                   # SQLAlchemy models
│   ├── schemas/
│   │   └── bot.py                   # Pydantic schemas
│   ├── services/                    # Business logic (future)
│   └── main.py                      # FastAPI application
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (running locally or remotely)
- pip (Python package manager)

## Installation

### 1. Clone the repository

```bash
cd scalper/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit the `.env` file and update the following variables:

```env
# Database Settings
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/scalper_bot

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 6. Create PostgreSQL database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE scalper_bot;

# Exit psql
\q
```

## Running the Application

### Development Mode

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly with Python:

```bash
python -m app.main
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs (Swagger UI): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint with API info
- `GET /health` - Health check endpoint

### Bots (`/api/v1/bots`)
- `GET /api/v1/bots` - List all bots (with optional filtering)
- `POST /api/v1/bots` - Create a new bot
- `GET /api/v1/bots/{bot_id}` - Get a specific bot
- `PUT /api/v1/bots/{bot_id}` - Update a bot
- `DELETE /api/v1/bots/{bot_id}` - Delete a bot
- `POST /api/v1/bots/{bot_id}/start` - Start a bot
- `POST /api/v1/bots/{bot_id}/stop` - Stop a bot
- `POST /api/v1/bots/{bot_id}/toggle` - Toggle bot status
- `POST /api/v1/bots/stop-all` - Emergency stop all bots
- `GET /api/v1/bots/statistics/summary` - Get statistics

### Activity Logs (`/api/v1/logs`)
- `GET /api/v1/logs` - List activity logs (with filtering)
- `POST /api/v1/logs` - Create an activity log
- `DELETE /api/v1/logs` - Clear all logs
- `GET /api/v1/logs/count` - Get log counts by level

## Database Models

### Bot
```python
{
    "id": "UUID",
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000.50,
    "sell_price": 46000.00,
    "trailing_percent": 1.5,
    "infinite_loop": true,
    "status": "ACTIVE",
    "pnl": 125.50,
    "total_trades": 10,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### ActivityLog
```python
{
    "id": "UUID",
    "bot_id": "UUID or null",
    "level": "INFO | SUCCESS | WARNING | ERROR | TELEGRAM",
    "message": "Log message",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {}
}
```

### Trade
```python
{
    "id": "UUID",
    "bot_id": "UUID",
    "symbol": "BTC/USDT",
    "side": "BUY | SELL",
    "quantity": 0.01,
    "price": 45000.50,
    "pnl": 25.50,
    "commission": 0.75,
    "exchange_order_id": "123456",
    "exchange": "Binance",
    "executed_at": "2024-01-01T00:00:00Z"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/scalper_bot` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

## Testing the API

### Using the Interactive Docs

1. Start the server
2. Navigate to http://localhost:8000/docs
3. Try out the endpoints directly from the browser

### Using cURL

**Create a bot:**
```bash
curl -X POST "http://localhost:8000/api/v1/bots" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000.50,
    "sell_price": 46000.00,
    "trailing_percent": 1.5,
    "infinite_loop": true
  }'
```

**Get all bots:**
```bash
curl "http://localhost:8000/api/v1/bots"
```

**Get activity logs:**
```bash
curl "http://localhost:8000/api/v1/logs?limit=10"
```

## Frontend Integration

The backend is configured with CORS to allow requests from the Next.js frontend running on `http://localhost:3000`.

To integrate with the frontend:

1. Update the frontend API client to use `http://localhost:8000/api/v1`
2. The backend will automatically create activity logs for bot operations
3. Use the WebSocket endpoints (coming soon) for real-time updates

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all endpoints
- Use async/await for all database operations

### Adding New Endpoints

1. Create schemas in `app/schemas/`
2. Add endpoint logic in `app/api/v1/endpoints/`
3. Register router in `app/api/v1/router.py`
4. Test using the interactive docs

## Troubleshooting

### Database Connection Error

If you get a database connection error:

1. Ensure PostgreSQL is running: `pg_ctl status` or `brew services list`
2. Check database exists: `psql -U postgres -l`
3. Verify credentials in `.env` file
4. Test connection: `psql -U postgres -d scalper_bot`

### Import Errors

If you get import errors:

1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.11+)

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

Or change the port in `.env`:

```env
PORT=8001
```

## Next Steps

- [ ] Set up Alembic for database migrations
- [ ] Add authentication and authorization
- [ ] Implement WebSocket endpoints for real-time updates
- [ ] Add Redis caching
- [ ] Set up Celery for background tasks
- [ ] Add comprehensive tests
- [ ] Set up Docker configuration
- [ ] Add logging and monitoring

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
