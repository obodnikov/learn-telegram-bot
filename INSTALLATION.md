# Installation Guide - Telegram Learning Bot

Complete step-by-step guide to install and run the bot from scratch.

---

## Prerequisites

- Python 3.10 or higher
- Telegram account
- OpenRouter API key (optional, for question generation)

---

## Quick Setup (Automated)

**For Linux/Mac users**, use the automated setup script:

```bash
git clone <repository-url>
cd learn-telegram-bot
bash scripts/setup.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Create .env file
- Seed database with topics
- Run diagnostics

**If you prefer manual setup**, or you're on Windows, follow the steps below.

---

## Manual Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd learn-telegram-bot
```

---

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required Python packages including:
- python-telegram-bot
- SQLAlchemy
- APScheduler
- OpenRouter client
- And more...

---

## Step 4: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions:
   - Choose a name for your bot (e.g., "My Learning Bot")
   - Choose a username (must end with 'bot', e.g., "mylearning_bot")
4. Save the **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## Step 5: Get OpenRouter API Key (Optional)

**Note**: Only needed if you want automatic question generation.

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up / log in
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Save the key (starts with `sk-or-v1-...`)

**Without API key**: You can still run the bot, but won't have automatic question generation.

---

## Step 6: Configure Environment

### Copy example configuration:
```bash
cp .env.example .env
```

### Edit `.env` file:
```bash
nano .env
# or use your preferred editor
```

### Required settings:
```env
# REQUIRED: Your Telegram bot token
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Database (default is fine for most users)
DATABASE_URL=sqlite:///./learning_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

### Optional settings (for question generation):
```env
# OpenRouter API (optional - for automatic question generation)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Scheduler (optional - enable automatic question generation)
ENABLE_SCHEDULER=false
QUESTION_GENERATION_SCHEDULE=0 */3 * * *
QUESTIONS_PER_RUN=5
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano).

---

## Step 7: Create Logs Directory

```bash
mkdir -p logs
```

---

## Step 8: Initialize Database and Seed Topics

This is the **critical step** that populates the database with topics!

```bash
python scripts/seed_topics.py
```

**Expected output**:
```
INFO - Connected to database: sqlite:///./learning_bot.db
INFO - Found 2 topics in configuration
INFO - Created new topic: Hungarian Vocabulary - Everyday Life (ID: 1)
INFO - Created new topic: Hungarian Literature and Culture (ID: 2)
INFO - Topic seeding completed successfully!
```

**If you see errors**: Check that your config files exist in `config/` directory.

---

## Step 9: Verify Installation

Run the diagnostic tool to verify everything is set up correctly:

```bash
python scripts/diagnose_database.py
```

**Expected output**:
```
✅ DIAGNOSIS: Database is healthy!
   2 active topics available
   Bot should work correctly
```

**If you see "No topics in database"**: Go back to Step 8 and run the seeding script.

---

## Step 10: Start the Bot

```bash
python main.py
```

**Expected startup logs**:
```
INFO - Starting Telegram Learning Bot...
INFO - ============================================================
INFO - Running startup validation checks...
INFO - ✓ Configurations loaded successfully
INFO - ✓ Example files validated
INFO - Initializing database: sqlite:///./learning_bot.db
INFO - Database absolute path: /full/path/to/learning_bot.db
INFO - Database file exists: True
INFO - Database initialized successfully - found 2 topics in database
INFO -   Topic: Hungarian Vocabulary - Everyday Life (Active: True)
INFO -   Topic: Hungarian Literature and Culture (Active: True)
INFO - LearningBot initialized successfully
INFO - Bot is running. Press Ctrl+C to stop.
```

**Key things to check**:
- ✅ "found 2 topics in database" - this means topics are loaded!
- ✅ Both topics show "Active: True"
- ✅ "Bot is running"

**If you see 0 topics**: The seeding step (Step 8) didn't work properly.

---

## Step 11: Test in Telegram

1. Open Telegram
2. Search for your bot by username (e.g., `@mylearning_bot`)
3. Click "Start" or send `/start`

**Try these commands**:
- `/start` - Welcome message
- `/help` - Show available commands
- `/topics` - **Should show 2 topic buttons!**
- `/stats` - Show your learning statistics

**If `/topics` shows "No topics available"**:
- Check the bot logs when you send the command
- You should see: `INFO - Topics query returned 2 topics (active_only=True)`
- If you see 0 topics, the database wasn't seeded properly

---

## Troubleshooting

### Problem: "No topics available yet"

**Solution**:
1. Stop the bot (Ctrl+C)
2. Run: `python scripts/seed_topics.py`
3. Verify: `python scripts/diagnose_database.py`
4. Should show: "2 active topics available"
5. Start bot again: `python main.py`

### Problem: "TELEGRAM_BOT_TOKEN not set"

**Solution**: Check your `.env` file has the token set correctly.

### Problem: Database errors

**Solution**:
```bash
# Delete database and start fresh
rm learning_bot.db

# Re-seed topics
python scripts/seed_topics.py

# Verify
python scripts/diagnose_database.py
```

### Problem: Import errors

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Bot starts but crashes immediately

**Solution**: Check logs in `logs/bot.log` for detailed error messages.

---

## Directory Structure After Installation

```
learn-telegram-bot/
├── venv/                    # Virtual environment (created in step 2)
├── logs/                    # Log files (created in step 7)
│   └── bot.log             # Bot logs
├── learning_bot.db          # SQLite database (created in step 8)
├── .env                     # Your configuration (created in step 6)
├── config/                  # Configuration files (should exist)
│   ├── topics.yaml
│   ├── prompts.yaml
│   ├── difficulty_levels.yaml
│   └── examples/
├── src/                     # Source code
├── scripts/                 # Utility scripts
└── requirements.txt         # Dependencies
```

---

## Quick Start Checklist

Use this checklist for fresh installations:

- [ ] Step 1: Clone repository
- [ ] Step 2: Create virtual environment (`python3 -m venv venv`)
- [ ] Step 3: Activate venv (`source venv/bin/activate`)
- [ ] Step 4: Install dependencies (`pip install -r requirements.txt`)
- [ ] Step 5: Create Telegram bot with @BotFather
- [ ] Step 6: Create `.env` file with bot token
- [ ] Step 7: Create logs directory (`mkdir -p logs`)
- [ ] Step 8: **Seed topics** (`python scripts/seed_topics.py`) ⚠️ CRITICAL
- [ ] Step 9: Verify installation (`python scripts/diagnose_database.py`)
- [ ] Step 10: Start bot (`python main.py`)
- [ ] Step 11: Test `/topics` command in Telegram

---

## Post-Installation: Adding Questions

The bot works with just topics, but questions make it functional!

### Option 1: Manual Question Generation (Recommended for testing)

If you have OpenRouter API key:

```python
# Start Python REPL
python3

# Run manual generation
>>> import asyncio
>>> from src.database.repository import Repository
>>> from src.utils.config_loader import ConfigLoader
>>> from src.services.llm_service import LLMService
>>> from src.services.question_generator import QuestionGenerator
>>> from src.services.example_parser import ExampleParser
>>> from src.services.scheduler import QuestionScheduler
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>>
>>> # Initialize services
>>> repo = Repository("sqlite:///./learning_bot.db")
>>> config = ConfigLoader("config")
>>> config.load_all()
>>> llm = LLMService(os.getenv('OPENROUTER_API_KEY'), 'anthropic/claude-3.5-sonnet')
>>> parser = ExampleParser()
>>> gen = QuestionGenerator(llm, config, parser)
>>> scheduler = QuestionScheduler(repo, gen, config)
>>>
>>> # Generate 5 questions for all topics
>>> count = asyncio.run(scheduler.run_manual_generation(count=5))
>>> print(f"Generated {count} questions")
```

### Option 2: Automatic Generation (Set and forget)

Enable in `.env`:
```env
ENABLE_SCHEDULER=true
OPENROUTER_API_KEY=sk-or-v1-your-key-here
QUESTION_GENERATION_SCHEDULE=0 */3 * * *  # Every 3 hours
QUESTIONS_PER_RUN=5
```

Restart bot, and it will generate questions automatically!

---

## Running in Production

Choose the deployment method that fits your environment:

### Option 1: systemd (Linux - Recommended)

**Best for**: Ubuntu, Debian, CentOS, Fedora, RHEL

#### Create systemd service file

Create `/etc/systemd/system/telegram-learning-bot.service`:

```ini
[Unit]
Description=Telegram Learning Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=your-username
Group=your-username
WorkingDirectory=/home/your-username/learn-telegram-bot
Environment="PATH=/home/your-username/learn-telegram-bot/venv/bin"
EnvironmentFile=/home/your-username/learn-telegram-bot/.env
ExecStart=/home/your-username/learn-telegram-bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/your-username/learn-telegram-bot/logs/bot.log
StandardError=append:/home/your-username/learn-telegram-bot/logs/bot.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/your-username/learn-telegram-bot/logs /home/your-username/learn-telegram-bot

[Install]
WantedBy=multi-user.target
```

**Replace `your-username` with your actual username!**

#### Enable and start the service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-learning-bot

# Start the service
sudo systemctl start telegram-learning-bot

# Check status
sudo systemctl status telegram-learning-bot
```

#### Manage the service

```bash
# View logs
sudo journalctl -u telegram-learning-bot -f

# Stop the bot
sudo systemctl stop telegram-learning-bot

# Restart the bot
sudo systemctl restart telegram-learning-bot

# Disable auto-start
sudo systemctl disable telegram-learning-bot
```

---

### Option 2: launchd (macOS - Recommended)

**Best for**: macOS

#### Create plist file

Create `~/Library/LaunchAgents/com.user.telegram-learning-bot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.telegram-learning-bot</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/learn-telegram-bot/venv/bin/python</string>
        <string>/Users/YOUR_USERNAME/learn-telegram-bot/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/learn-telegram-bot</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/YOUR_USERNAME/learn-telegram-bot/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/learn-telegram-bot/logs/bot.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/learn-telegram-bot/logs/bot.log</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
```

**Replace `YOUR_USERNAME` with your actual username!**

#### Load and start the service

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist

# Start the service
launchctl start com.user.telegram-learning-bot

# Check if running
launchctl list | grep telegram-learning-bot
```

#### Manage the service

```bash
# Stop the bot
launchctl stop com.user.telegram-learning-bot

# Restart (stop + start)
launchctl stop com.user.telegram-learning-bot
launchctl start com.user.telegram-learning-bot

# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist

# View logs
tail -f ~/learn-telegram-bot/logs/bot.log
```

---

### Option 3: Docker (Cross-platform)

**Best for**: Production deployments, cloud hosting, consistent environments

#### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Seed database (if not using volume)
# RUN python scripts/seed_topics.py

# Run the bot
CMD ["python", "main.py"]
```

#### Create docker-compose.yml

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: telegram-learning-bot
    restart: unless-stopped

    # Environment variables
    env_file:
      - .env

    # Persist database and logs
    volumes:
      - ./learning_bot.db:/app/learning_bot.db
      - ./logs:/app/logs
      - ./config:/app/config:ro

    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### Build and run with Docker

```bash
# Build the image
docker compose build

# Seed database first (important!)
docker compose run --rm telegram-bot python scripts/seed_topics.py

# Start the bot
docker compose up -d

# View logs
docker compose logs -f

# Stop the bot
docker compose down

# Restart the bot
docker compose restart
```

#### Docker management commands

```bash
# Check container status
docker compose ps

# View real-time logs
docker compose logs -f telegram-bot

# Execute commands in container
docker compose exec telegram-bot python scripts/diagnose_database.py

# Rebuild after code changes
docker compose build --no-cache
docker compose up -d

# Clean up
docker compose down --volumes
```

#### Docker with pre-seeded database

Alternative `Dockerfile` that seeds during build:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs and seed database
RUN mkdir -p logs && \
    python scripts/seed_topics.py

CMD ["python", "main.py"]
```

---

### Option 4: Docker with External Database (Advanced)

For production with PostgreSQL:

#### docker-compose.yml with PostgreSQL

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: telegram-bot-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: telegram_bot
      POSTGRES_USER: botuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U botuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  telegram-bot:
    build: .
    container_name: telegram-learning-bot
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://botuser:${DB_PASSWORD}@postgres:5432/telegram_bot
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro

volumes:
  postgres_data:
```

Update `.env`:
```env
DB_PASSWORD=your_secure_password_here
TELEGRAM_BOT_TOKEN=your_token
```

---

### Option 5: screen/tmux (Development/Quick Deploy)

**Best for**: Quick testing, development servers

#### Using screen

```bash
# Start screen session
screen -S telegram-bot

# Activate venv and run
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r telegram-bot
# Kill session: screen -X -S telegram-bot quit
```

#### Using tmux

```bash
# Start tmux session
tmux new -s telegram-bot

# Activate venv and run
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t telegram-bot
# Kill session: tmux kill-session -t telegram-bot
```

---

## Deployment Comparison

| Method | Platform | Auto-restart | Boot Start | Logs | Difficulty |
|--------|----------|--------------|------------|------|------------|
| **systemd** | Linux | ✅ | ✅ | journalctl | Easy |
| **launchd** | macOS | ✅ | ✅ | File | Medium |
| **Docker** | All | ✅ | ✅ | docker logs | Medium |
| **screen/tmux** | Linux/Mac | ❌ | ❌ | File | Easy |

**Recommendation**:
- **Linux servers**: Use systemd
- **macOS**: Use launchd
- **Cloud/Production**: Use Docker
- **Quick testing**: Use screen/tmux

---

## Updating Configuration

### Adding New Topics

1. Edit `config/topics.yaml`
2. Add your new topic configuration
3. Run: `python scripts/seed_topics.py`
4. Restart bot

### Changing Bot Behavior

- Edit configuration files in `config/`
- No need to seed again unless topics changed
- Restart bot to apply changes

---

## Getting Help

### Check Logs
```bash
tail -f logs/bot.log
```

### Run Diagnostics
```bash
python scripts/diagnose_database.py
```

### Common Log Messages

**Good**:
```
INFO - found 2 topics in database
INFO - Bot is running
INFO - Topics query returned 2 topics
```

**Bad**:
```
ERROR - No topics found in database
ERROR - TELEGRAM_BOT_TOKEN not set
ERROR - Database initialization failed
```

---

## Summary

The **most important steps** for a working bot:

1. ✅ Install dependencies
2. ✅ Set `TELEGRAM_BOT_TOKEN` in `.env`
3. ✅ **Run `python scripts/seed_topics.py`** ← THIS IS CRITICAL!
4. ✅ Verify with `python scripts/diagnose_database.py`
5. ✅ Start bot with `python main.py`

**The seeding step (step 8) is mandatory!** Without it, the database will be empty and the bot won't have any topics to show.

---

**Installation complete!** 🎉

Your bot should now be running and responding to commands in Telegram.
