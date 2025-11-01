# Quick Start Guide

Get your Telegram Learning Bot running in 5 minutes!

---

## For Experienced Users (TL;DR)

```bash
# Clone, setup, configure
git clone <repo-url> && cd learn-telegram-bot
bash scripts/setup.sh

# Edit .env with your bot token
nano .env

# Start bot
source venv/bin/activate
python main.py
```

Test: Send `/topics` in Telegram - should show 2 topics.

---

## For New Users (Step-by-Step)

### 1️⃣ Get a Telegram Bot Token (5 min)

1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Choose name: `My Learning Bot`
5. Choose username: `mylearning_bot` (must end with 'bot')
6. **Copy the token** (looks like: `123456:ABCdef...`)

### 2️⃣ Install the Bot (2 min)

**Option A: Automated (Linux/Mac)**
```bash
git clone <repository-url>
cd learn-telegram-bot
bash scripts/setup.sh
```

**Option B: Manual (All platforms)**
```bash
git clone <repository-url>
cd learn-telegram-bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p logs
cp .env.example .env
```

### 3️⃣ Configure Bot (1 min)

Edit `.env` file:
```bash
nano .env  # or use any text editor
```

Add your token:
```env
TELEGRAM_BOT_TOKEN=123456:ABCdef...  # Paste your token here
```

Save and exit (Ctrl+X, Y, Enter in nano).

### 4️⃣ Seed Database (1 min)

**THIS IS CRITICAL - DON'T SKIP!**

```bash
python scripts/seed_topics.py
```

Should see:
```
✓ Created new topic: Hungarian Vocabulary - Everyday Life
✓ Created new topic: Hungarian Literature and Culture
✓ Topic seeding completed successfully!
```

### 5️⃣ Generate Questions (2 min) ⚠️ NEW STEP!

**IMPORTANT**: Bot needs questions to work! This step is required.

**Get API Key** (if you don't have one):
1. Go to https://openrouter.ai/keys
2. Sign up and create API key
3. Add $5 credits

**Add to .env**:
```bash
nano .env
# Add line: OPENROUTER_API_KEY=sk-or-v1-your-key
# Save: Ctrl+X, Y, Enter
```

**Generate questions**:
```bash
python scripts/generate_questions.py --count 10
```

**Note**: Use batches of 10-15 for best results. For more questions, run multiple times.

Should see:
```
✓ Saved 10 questions for topic: Hungarian Vocabulary - Everyday Life
✓ Saved 10 questions for topic: Hungarian Literature and Culture
✓ Generation complete!
✓ Total questions generated: 20
```

### 6️⃣ Start Bot (1 min)

```bash
python main.py
```

Should see:
```
✓ Database initialized successfully - found 2 topics in database
✓ Bot is running. Press Ctrl+C to stop.
```

### 7️⃣ Test in Telegram (30 sec)

1. Open Telegram
2. Search for your bot (e.g., `@mylearning_bot`)
3. Click **Start**
4. Send: `/topics`
5. **Should see 2 topic buttons!** 🎉
6. **Click a topic** - Quiz should start! 🎉

---

## Troubleshooting

### ❌ "No questions available for this topic"

**Most common issue!** Bot needs questions.

**Fix:**
```bash
# 1. Get OpenRouter API key: https://openrouter.ai/keys
# 2. Add to .env: OPENROUTER_API_KEY=sk-or-v1-...
# 3. Generate questions:
python scripts/generate_questions.py --count 10

# 4. Verify:
python scripts/diagnose_database.py  # Should show questions > 0

# 5. Restart bot
python main.py
```

### ❌ "No topics available yet"

**Fix:**
```bash
# Stop bot (Ctrl+C)
python scripts/seed_topics.py
python scripts/diagnose_database.py  # Should show 2 topics
python main.py  # Restart
```

### ❌ "TELEGRAM_BOT_TOKEN not set"

**Fix:** Edit `.env` and add your token from BotFather.

### ❌ "OPENROUTER_API_KEY not found"

**Fix:**
```bash
# Get API key from https://openrouter.ai/keys
nano .env
# Add: OPENROUTER_API_KEY=sk-or-v1-your-key
```

### ❌ "Module not found"

**Fix:**
```bash
source venv/bin/activate  # Activate venv first!
pip install -r requirements.txt
```

### ❌ Bot doesn't respond

**Checklist:**
- [ ] Bot is running (you see "Bot is running" in terminal)
- [ ] Started bot in Telegram (click Start button)
- [ ] Using correct bot username
- [ ] Bot token is correct in .env

---

## What's Next?

### Add Questions (Optional)

Bot works without questions, but they make it useful!

**Option 1: Automatic (requires API key)**

Get OpenRouter API key from [openrouter.ai](https://openrouter.ai)

Add to `.env`:
```env
OPENROUTER_API_KEY=sk-or-v1-...
ENABLE_SCHEDULER=true
```

Restart bot - questions generate automatically every 3 hours.

**Option 2: Manual**

See [INSTALLATION.md](INSTALLATION.md#post-installation-adding-questions) for manual generation.

### Customize Topics

1. Edit `config/topics.yaml`
2. Run: `python scripts/seed_topics.py`
3. Restart bot

### Deploy to Server

See [INSTALLATION.md](INSTALLATION.md#running-in-production) for systemd setup.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and registration |
| `/help` | Show available commands |
| `/topics` | List topics and start quiz |
| `/stats` | View your learning statistics |
| `/cancel` | End current quiz session |

---

## File Locations

```
learn-telegram-bot/
├── .env              # Your configuration (EDIT THIS)
├── learning_bot.db   # Database (created automatically)
├── logs/bot.log      # Logs (check for errors)
├── main.py           # Start the bot
├── scripts/
│   ├── setup.sh              # Automated setup
│   ├── seed_topics.py        # Populate database
│   └── diagnose_database.py  # Check database health
└── config/           # Topics and prompts configuration
```

---

## Getting Help

### Check if bot sees topics:
```bash
python scripts/diagnose_database.py
```

### View logs:
```bash
tail -f logs/bot.log
```

### Common issues:
- **No topics**: Run `python scripts/seed_topics.py`
- **Bot not responding**: Check logs for errors
- **Import errors**: Activate venv: `source venv/bin/activate`

---

## Success Checklist

- [x] Created Telegram bot with @BotFather ✓
- [x] Cloned repository ✓
- [x] Installed dependencies ✓
- [x] Added bot token to .env ✓
- [x] Ran seed_topics.py (CRITICAL!) ✓
- [x] Diagnostic shows 2 topics ✓
- [x] Bot started without errors ✓
- [x] `/topics` shows 2 buttons in Telegram ✓

**All checked?** Your bot is working! 🎉

---

**Need more details?** See [INSTALLATION.md](INSTALLATION.md) for comprehensive guide.

**Found a bug?** Create an issue with logs from `logs/bot.log`.
