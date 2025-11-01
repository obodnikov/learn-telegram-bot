# Deployment Configurations

This directory contains production deployment configurations for various platforms.

---

## Files Overview

| File | Platform | Description |
|------|----------|-------------|
| `telegram-learning-bot.service` | Linux (systemd) | Systemd service unit file |
| `com.user.telegram-learning-bot.plist` | macOS (launchd) | Launch Agent configuration |
| `../Dockerfile` | Docker | Container image definition |
| `../docker-compose.yml` | Docker Compose | Multi-container orchestration |

---

## Quick Deploy

### Linux (systemd)

```bash
# 1. Edit service file with your username
sed -i 's/YOUR_USERNAME/your-actual-username/g' deployment/telegram-learning-bot.service

# 2. Copy to systemd directory
sudo cp deployment/telegram-learning-bot.service /etc/systemd/system/

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable telegram-learning-bot
sudo systemctl start telegram-learning-bot

# 4. Check status
sudo systemctl status telegram-learning-bot
```

### macOS (launchd)

```bash
# 1. Edit plist file with your username
sed -i '' 's/YOUR_USERNAME/your-actual-username/g' deployment/com.user.telegram-learning-bot.plist

# 2. Copy to LaunchAgents
cp deployment/com.user.telegram-learning-bot.plist ~/Library/LaunchAgents/

# 3. Load and start
launchctl load ~/Library/LaunchAgents/com.user.telegram-learning-bot.plist
launchctl start com.user.telegram-learning-bot

# 4. Check status
launchctl list | grep telegram-learning-bot
```

### Docker

```bash
# 1. Build image
docker compose build

# 2. Seed database (first time only)
docker compose run --rm telegram-bot python scripts/seed_topics.py

# 3. Start container
docker compose up -d

# 4. Check logs
docker compose logs -f
```

---

## Detailed Instructions

For comprehensive deployment instructions, see:
- **[INSTALLATION.md](../INSTALLATION.md#running-in-production)** - Full deployment guide
- **[QUICKSTART.md](../QUICKSTART.md)** - Quick start guide

---

## Platform-Specific Notes

### systemd (Linux)

**Features**:
- ✅ Auto-restart on crash
- ✅ Start on boot
- ✅ Integrated logging (journalctl)
- ✅ Security hardening options

**Requirements**:
- systemd-based Linux distribution
- Root/sudo access

**Log viewing**:
```bash
sudo journalctl -u telegram-learning-bot -f
```

---

### launchd (macOS)

**Features**:
- ✅ Auto-restart on crash
- ✅ Start on login
- ✅ File-based logging
- ✅ Native macOS integration

**Requirements**:
- macOS 10.10 or later
- User account (no root needed)

**Log viewing**:
```bash
tail -f ~/learn-telegram-bot/logs/bot.log
```

---

### Docker

**Features**:
- ✅ Isolated environment
- ✅ Easy updates
- ✅ Cross-platform
- ✅ Reproducible deployments

**Requirements**:
- Docker Engine 20.10+
- Docker Compose v2+

**Log viewing**:
```bash
docker compose logs -f telegram-bot
```

---

## Security Considerations

### systemd

The service file includes security hardening:
- `NoNewPrivileges=true` - Prevents privilege escalation
- `PrivateTmp=true` - Isolates /tmp directory
- `ProtectSystem=strict` - Read-only system directories
- `ProtectHome=read-only` - Read-only home directories
- `ReadWritePaths=...` - Explicit write permissions

### Docker

Security recommendations:
- Don't run as root inside container
- Use read-only volumes where possible
- Keep base image updated
- Scan for vulnerabilities

Add to Dockerfile:
```dockerfile
# Create non-root user
RUN useradd -m -u 1000 botuser
USER botuser
```

---

## Monitoring and Maintenance

### Health Checks

**systemd**:
```bash
systemctl status telegram-learning-bot
```

**launchd**:
```bash
launchctl list | grep telegram-learning-bot
ps aux | grep "main.py"
```

**Docker**:
```bash
docker compose ps
docker compose exec telegram-bot python scripts/diagnose_database.py
```

### Log Rotation

**systemd**: Automatic via journald

**launchd**: Manual or use logrotate

**Docker**: Configure in docker-compose.yml:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Updating the Bot

**systemd/launchd**:
```bash
# Pull updates
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart telegram-learning-bot  # Linux
# or
launchctl stop com.user.telegram-learning-bot  # macOS
launchctl start com.user.telegram-learning-bot
```

**Docker**:
```bash
# Pull updates
git pull

# Rebuild and restart
docker compose build --no-cache
docker compose up -d
```

---

## Troubleshooting

### Service won't start

**Check logs**:
- systemd: `sudo journalctl -u telegram-learning-bot -n 50`
- launchd: `cat ~/learn-telegram-bot/logs/bot.log`
- Docker: `docker compose logs`

**Common issues**:
1. Wrong username in config file
2. Virtual environment not activated
3. Missing .env file
4. Database not seeded
5. Permission issues

### Bot not responding

1. Check if process is running
2. Verify network connectivity
3. Check Telegram bot token
4. Review bot logs for errors

### Database issues

Run diagnostics:
```bash
# systemd
sudo -u YOUR_USERNAME /home/YOUR_USERNAME/learn-telegram-bot/venv/bin/python scripts/diagnose_database.py

# Docker
docker compose exec telegram-bot python scripts/diagnose_database.py
```

---

## Environment Variables

All deployment methods support loading from `.env` file:

```env
# Required
TELEGRAM_BOT_TOKEN=your_token_here

# Optional
DATABASE_URL=sqlite:///./learning_bot.db
OPENROUTER_API_KEY=your_api_key
ENABLE_SCHEDULER=false
LOG_LEVEL=INFO
```

**systemd**: Uses `EnvironmentFile` directive
**launchd**: Must be in .env file (loaded by Python)
**Docker**: Uses `env_file` in docker-compose.yml

---

## Performance Tuning

### Resource Limits (systemd)

Add to service file:
```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
```

### Container Resources (Docker)

Add to docker-compose.yml:
```yaml
services:
  telegram-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## Backup and Recovery

### What to backup

1. **Database**: `learning_bot.db`
2. **Configuration**: `.env`, `config/*.yaml`
3. **Logs** (optional): `logs/bot.log`

### Backup script

```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups/telegram-bot"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" \
    learning_bot.db \
    .env \
    config/
```

---

## Production Checklist

- [ ] Database seeded with topics
- [ ] `.env` configured with valid tokens
- [ ] Logs directory created and writable
- [ ] Service configured with correct username/paths
- [ ] Service enabled to start on boot
- [ ] Bot responds to `/topics` command
- [ ] Logs are being written
- [ ] Health check passes
- [ ] Backup strategy in place

---

**For more information**, see [INSTALLATION.md](../INSTALLATION.md).
