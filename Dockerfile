# Telegram Learning Bot - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY main.py .

# Create logs directory
RUN mkdir -p logs

# Note: Database seeding should be done separately:
# docker compose run --rm telegram-bot python scripts/seed_topics.py

# Run the bot
CMD ["python", "main.py"]
