# Deployment Guide

Complete guide for deploying the Telegram Learning Bot in production environments.

---

## Quick Navigation

- **[systemd (Linux)](#systemd-linux)** - Ubuntu, Debian, CentOS, Fedora, RHEL
- **[launchd (macOS)](#launchd-macos)** - macOS service management
- **[Docker](#docker)** - Containerized deployment (cross-platform)
- **[Docker + PostgreSQL](#docker-with-postgresql)** - Production setup with external DB
- **[screen/tmux](#screentmux)** - Quick deployment for testing

---

## Prerequisites

Before deploying, ensure you have completed:

1. ✅ **Installation** - Follow [INSTALLATION.md](INSTALLATION.md)
2. ✅ **Configuration** - Set up `.env` with bot token
3. ✅ **Database Seeding** - Run `python scripts/seed_topics.py`
4. ✅ **Testing** - Bot works with `/topics` command

---

## systemd (Linux)

**Best for**: Production servers running Ubuntu, Debian, CentOS, Fedora, RHEL

### Installation

```bash
# 1. Edit the service file with your username
cd ~/learn-telegram-bot
sed -i "s/YOUR_USERNAME/$(whoami)/g" deployment/telegram-learning-bot.service

# 2. Copy to systemd directory
sudo cp deployment/telegram-learning-bot.service /etc/systemd/system/

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable service (start on boot)
sudo systemctl enable telegram-learning-bot

# 5. Start the service
sudo systemctl start telegram-learning-bot

# 6. Check status
sudo systemctl status telegram-learning-bot
```

### Management Commands

```bash
# View live logs
sudo journalctl -u telegram-learning-bot -f

# View last 50 lines
sudo journalctl -u telegram-learning-bot -n 50

# Stop the bot
sudo systemctl stop telegram-learning-bot

# Restart the bot
sudo systemctl restart telegram-learning-bot

# Check if enabled
sudo systemctl is-enabled telegram-learning-bot

# Disable auto-start
sudo systemctl disable telegram-learning-bot
```

### Troubleshooting

**Service fails to start:**
```bash
# Check logs for errors
sudo journalctl -u telegram-learning-bot -n 100

# Verify paths in service file
cat /etc/systemd/system/telegram-learning-bot.service

# Test manually
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py
```

**Permission issues:**
```bash
# Ensure logs directory is writable
chmod 755 ~/learn-telegram-bot/logs

# Check file ownership
ls -la ~/learn-telegram-bot
```

---

## launchd (macOS)

**Best for**: macOS development machines or Mac Mini servers

### Installation

```bash
# 1. Edit the plist file with your username
cd ~/learn-telegram-bot
sed -i '' "s/YOUR_USERNAME/$(whoami)/g" deployment/com.user.telegram-learning-bot.plist

# 2. Copy to LaunchAgents
cp deployment/com.user.telegram-learning-bot.plist ~/Library/LaunchAgents/

# 3. Load the service
launchctl load ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist

# 4. Start the service
launchctl start com.user.telegram-learning-bot

# 5. Check status
launchctl list | grep telegram-learning-bot
```

### Management Commands

```bash
# View logs
tail -f ~/learn-telegram-bot/logs/bot.log

# Stop the service
launchctl stop com.user.telegram-learning-bot

# Restart (stop + start)
launchctl stop com.user.telegram-learning-bot
launchctl start com.user.telegram-learning-bot

# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist

# Reload configuration
launchctl unload ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist
launchctl load ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist
```

### Troubleshooting

**Service doesn't start:**
```bash
# Check if loaded
launchctl list | grep telegram

# Check for errors in system log
log show --predicate 'process == "launchctl"' --last 10m

# Verify plist syntax
plutil -lint ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist

# Test manually
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py
```

---

## Docker

**Best for**: Production deployments, cloud hosting, reproducible environments

### Prerequisites

```bash
# Install Docker
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS:
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
```

### Installation

```bash
# 1. Ensure .env file exists
cp .env.example .env
# Edit .env with your bot token

# 2. Build the image
docker compose build

# 3. Seed database (IMPORTANT!)
docker compose run --rm telegram-bot python scripts/seed_topics.py

# 4. Start the container
docker compose up -d

# 5. Check logs
docker compose logs -f
```

### Management Commands

```bash
# View logs (live)
docker compose logs -f telegram-bot

# View logs (last 100 lines)
docker compose logs --tail=100 telegram-bot

# Check container status
docker compose ps

# Stop the bot
docker compose down

# Restart the bot
docker compose restart telegram-bot

# Rebuild after code changes
docker compose build --no-cache
docker compose up -d

# Execute commands in container
docker compose exec telegram-bot python scripts/diagnose_database.py

# Shell into container
docker compose exec telegram-bot /bin/bash
```

### Updating the Bot

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose build
docker compose up -d
```

### Troubleshooting

**Container exits immediately:**
```bash
# Check logs
docker compose logs telegram-bot

# Check if .env is properly loaded
docker compose config

# Test image
docker compose run --rm telegram-bot python -c "import sys; print(sys.version)"
```

**Database issues:**
```bash
# Check if database file exists
ls -la learning_bot.db

# Re-seed database
docker compose run --rm telegram-bot python scripts/seed_topics.py

# Run diagnostics
docker compose exec telegram-bot python scripts/diagnose_database.py
```

---

## Docker with PostgreSQL

**Best for**: Production environments requiring high performance and reliability

### Setup

```bash
# 1. Create production docker-compose
cat > docker-compose.prod.yml << 'EOF'
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
EOF

# 2. Update .env
cat >> .env << 'EOF'
DB_PASSWORD=your_secure_password_here
EOF

# 3. Start services
docker compose -f docker-compose.prod.yml up -d

# 4. Wait for PostgreSQL to be ready
sleep 10

# 5. Seed database
docker compose -f docker-compose.prod.yml exec telegram-bot python scripts/seed_topics.py
```

### Management

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Backup database
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U botuser telegram_bot > backup.sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T postgres psql -U botuser telegram_bot < backup.sql

# Stop services
docker compose -f docker-compose.prod.yml down
```

---

## screen/tmux

**Best for**: Quick testing, development environments

### Using screen

```bash
# Start screen session
screen -S telegram-bot

# Run bot
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py

# Detach from session: Ctrl+A, then D

# Reattach to session
screen -r telegram-bot

# List sessions
screen -ls

# Kill session
screen -X -S telegram-bot quit
```

### Using tmux

```bash
# Start tmux session
tmux new -s telegram-bot

# Run bot
cd ~/learn-telegram-bot
source venv/bin/activate
python main.py

# Detach from session: Ctrl+B, then D

# Reattach to session
tmux attach -t telegram-bot

# List sessions
tmux ls

# Kill session
tmux kill-session -t telegram-bot
```

---

## Comparison Table

| Feature | systemd | launchd | Docker | screen/tmux |
|---------|---------|---------|--------|-------------|
| **Platform** | Linux | macOS | All | Linux/Mac |
| **Auto-restart** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Boot start** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Log management** | ✅ journalctl | ⚠️ File | ✅ Built-in | ⚠️ File |
| **Resource limits** | ✅ Yes | ⚠️ Limited | ✅ Yes | ❌ No |
| **Isolation** | ⚠️ Partial | ❌ No | ✅ Full | ❌ No |
| **Setup complexity** | Easy | Medium | Medium | Very Easy |
| **Production ready** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |

**Recommendations:**
- **Production Linux**: systemd
- **Production macOS**: launchd
- **Production Cloud**: Docker
- **Development**: screen/tmux
- **High availability**: Docker + PostgreSQL

---

## Post-Deployment Checklist

- [ ] Service is running
- [ ] Bot responds to `/start` in Telegram
- [ ] Bot responds to `/topics` (shows 2 topics)
- [ ] Logs are being written
- [ ] Service restarts automatically on crash
- [ ] Service starts on boot
- [ ] Database is backed up regularly
- [ ] Monitoring is in place
- [ ] Error alerts are configured

---

## Monitoring

### Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash
# Health check for Telegram Learning Bot

# Check if process is running
if pgrep -f "python main.py" > /dev/null; then
    echo "✓ Bot process is running"
else
    echo "✗ Bot process is NOT running"
    exit 1
fi

# Check database
if python scripts/diagnose_database.py > /dev/null 2>&1; then
    echo "✓ Database is healthy"
else
    echo "✗ Database check failed"
    exit 1
fi

echo "✓ All checks passed"
exit 0
```

### Monitoring with systemd

Add to service file:
```ini
[Service]
# Send heartbeat every 30 seconds
WatchdogSec=30

# Notify systemd when ready
Type=notify
```

### Monitoring with Docker

Add healthcheck to docker-compose.yml:
```yaml
services:
  telegram-bot:
    healthcheck:
      test: ["CMD", "python", "scripts/health_check.py"]
      interval: 1m
      timeout: 10s
      retries: 3
```

---

## Backup Strategy

### What to Backup

1. **Database**: `learning_bot.db` (or PostgreSQL dump)
2. **Configuration**: `.env`, `config/*.yaml`
3. **Logs** (optional): `logs/bot.log`

### Backup Script

```bash
#!/bin/bash
# Automated backup script

BACKUP_DIR="$HOME/backups/telegram-bot"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
cd ~/learn-telegram-bot
tar -czf "$BACKUP_FILE" \
    learning_bot.db \
    .env \
    config/

# Keep only last 7 backups
ls -t "$BACKUP_DIR"/backup-*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup created: $BACKUP_FILE"
```

### Automated Backups

**Using cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

---

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong bot token** - Generate new token if compromised
3. **Limit file permissions**:
   ```bash
   chmod 600 .env
   chmod 700 scripts/*.sh
   ```
4. **Use firewall** - Block unnecessary ports
5. **Keep system updated**:
   ```bash
   sudo apt update && sudo apt upgrade  # Ubuntu/Debian
   ```
6. **Enable systemd security features** (see service file)
7. **Use PostgreSQL for production** instead of SQLite
8. **Regular backups** - Automate with cron
9. **Monitor logs** - Set up alerts for errors
10. **Update dependencies**:
    ```bash
    pip install --upgrade -r requirements.txt
    ```

---

## Performance Tuning

### Resource Limits (systemd)

```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
TasksMax=100
```

### Docker Resources

```yaml
services:
  telegram-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

---

## Troubleshooting Common Issues

### Bot not responding

1. Check if service is running
2. Check logs for errors
3. Verify bot token
4. Test network connectivity
5. Check Telegram API status

### High memory usage

1. Check for memory leaks in logs
2. Set memory limits
3. Consider using PostgreSQL
4. Review question generation schedule

### Database locked (SQLite)

1. Check for multiple bot instances
2. Consider PostgreSQL for production
3. Restart the bot

---

## Getting Help

- **Deployment issues**: See [deployment/README.md](deployment/README.md)
- **General help**: See [INSTALLATION.md](INSTALLATION.md)
- **Quick start**: See [QUICKSTART.md](QUICKSTART.md)
- **Diagnostics**: Run `python scripts/diagnose_database.py`
- **Logs**: Check bot logs for detailed errors

---

**Ready to deploy!** Choose your platform above and follow the instructions.
