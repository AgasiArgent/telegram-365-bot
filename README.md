# Telegram 365 Bot

A Telegram bot that sends daily messages to users for 365 days, with an admin panel for content management.

## Features

- **Daily Message Delivery**: Users receive a unique message each day for 365 days
- **Timezone-Aware**: Messages are delivered at the configured time in each user's timezone
- **Admin Telegram Commands**: Manage content directly from Telegram
- **Web Admin Panel**: Browser-based dashboard for managing all 365 messages
- **Cycle Restart**: After day 365, the cycle automatically restarts from day 1

## Technology Stack

- **Backend**: Python 3.11+, aiogram 3.x (Telegram), Flask (Web)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Scheduler**: APScheduler for timezone-aware message delivery
- **Frontend**: HTML/CSS with Jinja2 templates

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd telegram-365-bot
   chmod +x init.sh
   ./init.sh
   ```

2. **Configure environment**:
   Edit `.env` file with your credentials:
   - `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/BotFather)
   - `DATABASE_URL`: PostgreSQL connection string
   - `ADMIN_PASSWORD`: Secret password for Telegram admin access
   - `WEB_ADMIN_PASSWORD`: Password for web panel login

3. **Start the bot**:
   ```bash
   source venv/bin/activate
   python3 src/main.py
   ```

## Usage

### For Users

1. Start a conversation with the bot
2. Send `/start` command
3. Receive welcome message
4. Receive daily messages automatically at the scheduled time

### For Admins (Telegram)

1. Send `/admin <password>` to unlock admin mode
2. Available commands:
   - `/welcome` - View current welcome message
   - `/setwelcome <text>` - Update welcome message
   - `/day <number>` - View message for specific day (1-365)
   - `/setday <number> <text>` - Update message for specific day

### For Admins (Web Panel)

1. Navigate to `http://localhost:5000`
2. Login with `WEB_ADMIN_PASSWORD`
3. Dashboard shows all 365 days with edit options
4. Edit individual day messages with:
   - Text content
   - Send time
   - Preview functionality

## Project Structure

```
telegram-365-bot/
├── src/
│   ├── main.py           # Application entry point
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py   # Telegram command handlers
│   │   └── middlewares.py
│   ├── web/
│   │   ├── __init__.py
│   │   ├── routes.py     # Flask routes
│   │   └── templates/    # Jinja2 templates
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── jobs.py       # APScheduler jobs
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py     # SQLAlchemy models
│   │   └── queries.py    # Database operations
│   └── config.py         # Configuration management
├── tests/
├── requirements.txt
├── init.sh
├── .env.example
└── README.md
```

## Database Schema

### Users Table
- `id`: Primary key
- `telegram_id`: Unique Telegram user ID
- `username`: Telegram username (optional)
- `timezone`: User's timezone (default: UTC)
- `current_day`: Current day in the 365-day cycle
- `started_at`: When user first started
- `last_message_date`: Last message delivery date
- `is_active`: Whether user is active

### Messages Table
- `id`: Primary key
- `day_number`: Day number (1-365, unique)
- `content`: Message text (max 4096 chars)
- `send_time`: Daily send time (default: 09:00)

### Settings Table
- `id`: Primary key
- `key`: Setting name (e.g., 'welcome_message')
- `value`: Setting value

### Admins Table
- `id`: Primary key
- `telegram_id`: Telegram user ID with admin access
- `granted_at`: When admin access was granted

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Required |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `ADMIN_PASSWORD` | Secret password for Telegram admin | Required |
| `WEB_ADMIN_PASSWORD` | Password for web panel | Required |
| `SECRET_KEY` | Flask session secret key | Required |
| `FLASK_HOST` | Web server host | 0.0.0.0 |
| `FLASK_PORT` | Web server port | 5000 |

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
alembic upgrade head
```

## License

MIT License
