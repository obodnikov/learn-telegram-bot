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

**⚠️ IMPORTANT**: The bot needs questions to function! Without questions, users can see topics but cannot start quizzes.

### Understanding Question Generation

**Current Status After Installation**:
- ✅ Bot is installed
- ✅ Topics are seeded (2 topics)
- ❌ Questions = 0 (database is empty)
- ❌ Quizzes won't work yet

**What Happens Without Questions**:
1. User sends `/topics` → ✅ Works (shows 2 topics)
2. User selects a topic → ❌ Fails ("No questions available for this topic")

**You MUST add questions before the bot is useful!**

---

### Option 1: Manual Question Generation (Recommended)

**Best for**: Initial setup, testing, controlled generation

**Requirements**:
- OpenRouter API key (get at https://openrouter.ai/keys)
- ~$0.02-0.05 per 10 questions generated
- Takes 30-60 seconds per topic

#### Step 1: Get OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up / log in
3. Go to https://openrouter.ai/keys
4. Create new key
5. Add $5 credits (plenty for testing)
6. Copy the key (starts with `sk-or-v1-...`)

#### Step 2: Add to .env

```bash
# Edit .env file
nano .env

# Add this line:
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Save and exit (Ctrl+X, Y, Enter)
```

#### Step 3: Generate Questions

**Using the convenience script (easiest)**:
```bash
# Generate 10 questions per topic (20 total)
python scripts/generate_questions.py --count 10

# Or generate for specific topic
python scripts/generate_questions.py --topic 1 --count 15

# Or just use defaults (5 per topic)
python scripts/generate_questions.py
```

**Important**: Use batches of 10-15 questions for best results. Larger batches (25+) may fail due to LLM response size limits. To generate many questions, run the script multiple times.

**Expected output**:
```
INFO - Connected to database: sqlite:///./learning_bot.db
INFO - Using LLM model: anthropic/claude-3.5-sonnet
INFO - Generating 10 questions per topic (all active topics)
INFO - Starting generation... (this may take 30-60 seconds per topic)
INFO - Generating 10 questions for topic: Hungarian Vocabulary - Everyday Life
INFO - Saved 10 questions for topic: Hungarian Vocabulary - Everyday Life
INFO - Generating 10 questions for topic: Hungarian Literature and Culture
INFO - Saved 10 questions for topic: Hungarian Literature and Culture
INFO - ✓ Generation complete!
INFO - ✓ Total questions generated: 20
```

#### Step 4: Verify

```bash
# Check database
python scripts/diagnose_database.py

# Should now show:
# Total questions: 20 (or however many you generated)
```

#### Step 5: Test the Bot

```bash
# Start/restart bot
python main.py

# In Telegram:
# 1. Send /topics
# 2. Select a topic
# 3. Quiz should start! ✓
```

---

### Option 2: Automatic Generation (Set and Forget)

**Best for**: Production, continuous operation, hands-off

**How it works**:
- Bot generates questions automatically on a schedule
- Default: Every 3 hours, 5 questions per topic
- Runs in background while bot is active
- Questions accumulate over time

#### Enable Automatic Generation

Add to `.env`:
```env
# Enable scheduler
ENABLE_SCHEDULER=true

# Your API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Schedule (cron format)
QUESTION_GENERATION_SCHEDULE=0 */3 * * *  # Every 3 hours

# Questions per run
QUESTIONS_PER_RUN=5  # 5 per topic = 10 total every 3 hours
```

#### Schedule Examples

```bash
# Every 3 hours (default)
QUESTION_GENERATION_SCHEDULE=0 */3 * * *

# Every 6 hours
QUESTION_GENERATION_SCHEDULE=0 */6 * * *

# Every day at 2 AM
QUESTION_GENERATION_SCHEDULE=0 2 * * *

# Twice daily (9 AM and 9 PM)
QUESTION_GENERATION_SCHEDULE=0 9,21 * * *

# Every hour (not recommended - costly!)
QUESTION_GENERATION_SCHEDULE=0 * * * *
```

#### Start Bot with Scheduler

```bash
python main.py

# You should see:
# INFO - Scheduler initialized
# INFO - Question generation scheduler started
# INFO - Bot is running. Press Ctrl+C to stop.
```

#### Cost Estimate

With default settings:
- 2 topics × 5 questions = 10 questions per run
- Every 3 hours = 8 runs per day
- 10 × 8 = 80 questions per day
- **Cost**: ~$0.05-0.10 per day (~$1.50-3.00 per month)

---

### Option 3: Hybrid Approach (Recommended for Production)

**Best strategy**:

1. **Initial setup**: Manual generation
   ```bash
   # Generate initial questions (run multiple times for more)
   python scripts/generate_questions.py --count 10
   python scripts/generate_questions.py --count 10
   python scripts/generate_questions.py --count 10
   # Now you have 60 questions total (30 per topic)
   ```

2. **Verify bot works**:
   - Test quizzes in Telegram
   - Confirm question quality
   - Adjust if needed

3. **Enable scheduler**: For ongoing generation
   ```env
   ENABLE_SCHEDULER=true
   OPENROUTER_API_KEY=sk-or-v1-...
   QUESTION_GENERATION_SCHEDULE=0 */6 * * *  # Every 6 hours
   QUESTIONS_PER_RUN=3  # Slower growth, lower cost
   ```

4. **Monitor and adjust**:
   - Check costs after first week
   - Adjust schedule/count as needed
   - Review question quality periodically

---

### Comparison Table

| Method | When | Cost | Control | Setup |
|--------|------|------|---------|-------|
| **Manual** | On-demand | Pay per use | Full control | Easy |
| **Automatic** | Scheduled | Ongoing | Set & forget | Medium |
| **Hybrid** | Both | Flexible | Best of both | Easy |

**Recommendation**: Start with manual generation (50-100 questions), then enable scheduler for growth.

---

### Troubleshooting Question Generation

**"OPENROUTER_API_KEY not found"**
- Check `.env` file has the key
- Make sure it starts with `sk-or-v1-`
- No quotes around the key in .env

**"No questions generated"**
- Check you have credits in OpenRouter account
- Verify API key is valid
- Check logs for errors: `tail -f logs/bot.log`

**"Generation takes too long"**
- Normal! ~30-60 seconds per topic per run
- LLM needs time to generate quality questions
- Be patient during first generation

**"Questions are low quality"**
- Check example files in `config/examples/`
- Review prompts in `config/prompts.yaml`
- Consider using different model (see OPENROUTER_MODEL)

**"Bot still says no questions"**
- Run diagnostics: `python scripts/diagnose_database.py`
- Check if questions are in database
- Restart bot after generating questions

---

### Next Steps After Adding Questions

Once you have questions in the database:

1. ✅ **Test the bot thoroughly**
   - Try all topics
   - Answer questions
   - Check explanations
   - Verify spaced repetition

2. ✅ **Deploy to production** (see [DEPLOYMENT.md](DEPLOYMENT.md))
   - Choose: systemd, Docker, or launchd
   - Set up auto-start
   - Enable scheduler if desired

3. ✅ **Monitor usage**
   - Check logs regularly
   - Review API costs
   - Adjust generation schedule

4. ✅ **Gather feedback**
   - Ask users about question quality
   - Adjust difficulty if needed
   - Add more topics as needed

---

**Ready to generate questions?** Follow Option 1 above to get started!

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
