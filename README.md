# Telegram 365 Bot

Telegram-бот, который отправляет пользователям уникальное сообщение каждый день на протяжении 365 дней. Включает веб-админку для управления контентом.

## Что умеет

- **365 дней контента** — каждый день новое сообщение
- **Учёт таймзон** — сообщения приходят в нужное время пользователя
- **Автоматический цикл** — после 365 дня начинается заново
- **Админка в Telegram** — управление через команды бота
- **Веб-админка** — удобный интерфейс для редактирования всех 365 сообщений

## Быстрый старт (Docker)

```bash
# 1. Клонируем
git clone https://github.com/AgasiArgent/telegram-365-bot
cd telegram-365-bot

# 2. Создаём .env файл
cp .env.example .env

# 3. Вписываем токен бота (получить у @BotFather)
nano .env  # или любой редактор

# 4. Запускаем
docker compose up
```

Готово! Бот работает, админка доступна на http://localhost:5000

## Запуск без Docker

```bash
# 1. Клонируем
git clone https://github.com/AgasiArgent/telegram-365-bot
cd telegram-365-bot

# 2. Установка
chmod +x init.sh
./init.sh

# 3. Настройка
cp .env.example .env
nano .env  # вписать TELEGRAM_BOT_TOKEN

# 4. Запуск
source venv/bin/activate
python3 src/main.py
```

## Настройка (.env)

| Переменная           | Описание                       | По умолчанию    |
| -------------------- | ------------------------------ | --------------- |
| `TELEGRAM_BOT_TOKEN` | Токен от @BotFather            | **обязательно** |
| `ADMIN_PASSWORD`     | Пароль для админ-команд в боте | `admin123`      |
| `WEB_ADMIN_PASSWORD` | Пароль для веб-админки         | `webadmin123`   |
| `SCHEDULER_TIMEZONE` | Таймзона планировщика          | `UTC`           |

## Использование

### Для пользователей

1. Найти бота в Telegram
2. Нажать `/start`
3. Получать сообщения каждый день

### Админ-команды в Telegram

```
/admin <пароль>     — получить админ-доступ
/welcome            — посмотреть приветствие
/setwelcome <текст> — изменить приветствие
/day <номер>        — посмотреть сообщение дня (1-365)
/setday <номер> <текст> — изменить сообщение дня
```

### Веб-админка

1. Открыть http://localhost:5000
2. Ввести `WEB_ADMIN_PASSWORD`
3. Редактировать любой из 365 дней:
   - Текст сообщения
   - Время отправки
   - Превью перед сохранением

## Архитектура

```
src/
├── main.py          # Точка входа
├── config.py        # Конфигурация
├── bot/             # Telegram бот (aiogram)
│   ├── handlers.py  # Обработчики команд
│   └── middlewares.py
├── web/             # Веб-админка (Flask)
│   ├── routes.py
│   └── templates/
├── scheduler/       # Планировщик (APScheduler)
│   └── jobs.py
└── database/        # БД (SQLAlchemy)
    ├── models.py
    └── queries.py
```

## Стек

- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot API
- **Flask** — веб-админка
- **PostgreSQL** — база данных
- **APScheduler** — планировщик сообщений
- **Docker** — контейнеризация

## Лицензия

MIT
