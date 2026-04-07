# CryptoRadar 🚨

Real-time cryptocurrency price tracking and alert system. Set price thresholds for your favorite coins and receive instant Telegram notifications when prices cross them.

## Features

- Real-time price tracking for 10+ cryptocurrencies via CoinGecko
- JWT-based user authentication
- Custom price alerts (above/below threshold)
- Instant Telegram notifications
- Automatic price updates every 5 minutes
- Redis caching to handle rate limits
- RESTful API with automatic Swagger documentation

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — persistent storage for users and alerts
- **Redis** — price caching and Celery message broker
- **Celery + Celery Beat** — background task scheduling
- **SQLAlchemy** — ORM and database management
- **JWT** — authentication
- **Docker Compose** — infrastructure
- **httpx** — HTTP client
- **Telegram Bot API** — notifications

## Architecture

```
CoinGecko API
     ↓
Celery Beat (every 5 min)
     ↓
Redis Cache
     ↓
FastAPI ←── Users
     ↓
Celery Beat (every 1 min)
     ↓
Telegram Notifications
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Telegram Bot token (via @BotFather)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/cryptoradar.git
cd cryptoradar
```

**2. Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Set up environment variables**

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
DATABASE_URL=postgresql://cryptoradar:password@localhost:5432/cryptoradar
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
TELEGRAM_TOKEN=your-telegram-bot-token
```

**4. Start infrastructure**

```bash
docker compose up -d
```

**5. Start the API**

```bash
uvicorn api.main:app --reload --port 8000
```

**6. Start Celery Worker and Beat**

```bash
# Price collector
celery -A collector.tasks.celery_app worker --loglevel=info
celery -A collector.tasks.celery_app beat --loglevel=info

# Alert checker
celery -A alerts.tasks.celery_app worker --loglevel=info
celery -A alerts.tasks.celery_app beat --loglevel=info
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger UI.

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /auth/register | Register new user | No |
| POST | /auth/login | Login, get JWT token | No |
| GET | /prices/ | Get all tracked prices | No |
| GET | /prices/{coin} | Get specific coin price | No |
| POST | /alerts/ | Create price alert | Yes |
| GET | /alerts/ | List your alerts | Yes |
| DELETE | /alerts/{id} | Deactivate alert | Yes |
| GET | /health | Health check | No |

## How It Works

**Price Collection** — Celery Beat fetches prices from CoinGecko every 5 minutes and stores them in Redis with a 10-minute TTL. This ensures we never hit rate limits regardless of user traffic.

**Alert Checking** — Every minute, Celery checks all active alerts against current Redis prices. When a threshold is crossed, a Telegram message is sent and the alert is deactivated.

**Authentication** — JWT tokens are issued on login and verified on every protected request without database queries.

**Soft Delete** — Alerts are never deleted from the database. Setting `is_active = False` hides them from users while preserving history.

## Project Structure

```
cryptoradar/
├── api/
│   ├── models/          # SQLAlchemy database models
│   ├── routes/          # FastAPI route handlers
│   ├── schemas/         # Pydantic request/response schemas
│   ├── exceptions.py    # Centralized HTTP exceptions
│   ├── security.py      # JWT and password hashing
│   └── main.py          # FastAPI app entry point
├── alerts/
│   ├── tasks.py         # Celery alert checker task
│   └── notifier.py      # Telegram notification sender
├── collector/
│   └── tasks.py         # Celery price collector task
├── shared/
│   ├── config.py        # Pydantic settings
│   ├── database.py      # SQLAlchemy engine and session
│   └── redis_client.py  # Redis connection
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| REDIS_URL | Redis connection string | Yes |
| SECRET_KEY | JWT signing key | Yes |
| TELEGRAM_TOKEN | Telegram bot token | Yes |
| DEBUG | Enable debug mode | No |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT expiry (default: 30) | No |
| PRICE_UPDATE_INTERVAL | Collection interval in seconds (default: 300) | No |

## Tracked Coins

Bitcoin, Ethereum, Solana, Cardano, Polkadot, Chainlink, Avalanche, Uniswap, Litecoin, Dogecoin

## License

MIT
