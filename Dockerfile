# Telegram 365 Bot - Docker Image
FROM python:3.11-alpine

# Install system dependencies for psycopg2
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies + psycopg2 for PostgreSQL
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# Copy application code
COPY src/ ./src/
COPY .env.example .env.example

# Create non-root user for security
RUN adduser -D botuser
USER botuser

# Expose web admin port
EXPOSE 5000

# Run the bot
CMD ["python", "src/main.py"]
