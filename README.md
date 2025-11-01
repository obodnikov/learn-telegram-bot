# Telegram Learning Bot

An intelligent Telegram bot for learning foreign languages, historical facts, and other educational topics using LLM-powered question generation with spaced repetition.

## 🚀 Quick Links

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment (systemd, Docker, launchd)
- **[Troubleshooting](BUGFIX_TOPICS.md)** - Common issues and solutions

## Features

- 🧠 **LLM-Powered Questions**: Uses OpenRouter API to generate high-quality questions
- 📚 **Multiple Topics**: Support for languages, history, and custom topics
- 🎯 **Spaced Repetition**: Smart algorithm tracks progress and repeats missed questions
- 📝 **Example-Based Learning**: Configure question style using example files
- 🌍 **Multilingual**: Support for any language pair (e.g., Hungarian/Russian)
- 📊 **Progress Tracking**: Analytics on question performance and user learning
- ⚙️ **Highly Configurable**: YAML-based topic and prompt configuration

## Project Status

Currently ready for **Phase 5: Analytics & Question Refinement** (Optional)

### Phase 1: Core Infrastructure & Validation ✅
- [x] Project structure
- [x] Configuration system (YAML-based)
- [x] Example file validation
- [x] Logging infrastructure
- [x] Startup validation
- [x] Custom exception handling

### Phase 2: Database & LLM Integration ✅
- [x] SQLAlchemy models with relationships
- [x] Alembic migration system
- [x] Repository pattern with CRUD operations
- [x] Spaced repetition algorithm (3-tier priority)
- [x] OpenRouter LLM integration
- [x] Question generator (4 modes)
- [x] Example parser service

### Phase 3: Telegram Bot Handlers ✅
- [x] Bot initialization and session management
- [x] Command handlers (/start, /help, /topics, /stats, /cancel)
- [x] Quiz interaction handlers
- [x] Inline keyboard callbacks (topic selection, answers, next question)
- [x] Progress tracking integration
- [x] User statistics display

### Phase 4: Question Generation & Scheduling ✅
- [x] APScheduler integration for automated generation
- [x] Cron-based scheduling (configurable intervals)
- [x] Background question generation jobs
- [x] Topic seeding script
- [x] Manual generation API
- [x] Environment-based scheduler control

See [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md), [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md), [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md), and [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) for details.

### Future Enhancements (Optional)
- [ ] Phase 5: Advanced analytics and question quality management
- [ ] Admin commands for question review
- [ ] Automatic quality scoring and filtering

## Installation

**⚠️ IMPORTANT**: For complete installation instructions, see **[INSTALLATION.md](INSTALLATION.md)**

### Quick Install

```bash
# 1. Clone and setup
git clone <repository-url>
cd learn-telegram-bot
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

# 4. Create logs directory
mkdir -p logs

# 5. CRITICAL: Seed database with topics
python scripts/seed_topics.py

# 6. Verify installation
python scripts/diagnose_database.py

# 7. Run bot
python main.py
```

**👉 Step 5 (seeding topics) is mandatory!** Without it, the bot will have no topics to display.

See **[INSTALLATION.md](INSTALLATION.md)** for detailed step-by-step guide with troubleshooting.

## Configuration

### 1. Environment Variables (.env)

```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### 2. Topics Configuration (config/topics.yaml)

Define learning topics with:
- Target/native languages
- Difficulty levels (beginner, intermediate, advanced, expert)
- Example files for question style
- Generation modes (augment, template, hybrid)

### 3. Example Questions (config/examples/*.json)

Provide example questions to guide LLM generation:
- Question structure
- Answer choices
- Bilingual explanations
- Difficulty level

## Usage

### Quick Start

```bash
# 1. Seed topics (required - first time only)
python scripts/seed_topics.py

# 2. Generate initial questions (required for quizzes)
python scripts/generate_questions.py --count 10

# 3. Run the bot
python main.py
```

**⚠️ Important**: The bot needs questions to function! See [Question Generation](#question-generation) below.

### Running the Bot

```bash
# Make sure topics are seeded
python scripts/seed_topics.py

# Verify setup
python scripts/diagnose_database.py

# Start the bot
python main.py
```

The bot will:
1. Validate all configuration files
2. Initialize the database (create tables if needed)
3. Load topics and prompts
4. Start polling for Telegram messages
5. Start question generation scheduler (if enabled)

**Telegram Commands:**
- `/start` - Register and welcome message
- `/help` - Show available commands
- `/topics` - List topics and start quiz (requires questions!)
- `/stats` - View learning statistics
- `/cancel` - End current quiz session

---

## Question Generation

**Status After Installation**: 0 questions in database

The bot can show topics but **cannot start quizzes** without questions!

### Option 1: Manual Generation (Recommended)

Generate questions on-demand using the convenience script:

```bash
# Generate 10 questions per topic
python scripts/generate_questions.py --count 10

# Generate for specific topic
python scripts/generate_questions.py --topic 1 --count 15

# Use defaults (5 per topic)
python scripts/generate_questions.py
```

**Requirements**:
- OpenRouter API key (get at https://openrouter.ai/keys)
- Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-your-key`
- ~$0.02-0.05 per 10 questions

### Option 2: Automatic Generation

Enable continuous generation in `.env`:

```env
ENABLE_SCHEDULER=true
OPENROUTER_API_KEY=sk-or-v1-your-key
QUESTION_GENERATION_SCHEDULE=0 */3 * * *  # Every 3 hours
QUESTIONS_PER_RUN=5  # 5 per topic
```

Then restart the bot. Questions will generate automatically.

**Cost estimate**: ~$0.05-0.10 per day with default settings.

### Verify Questions

```bash
# Check how many questions you have
python scripts/diagnose_database.py

# Should show:
#   Total questions: 20 (or whatever you generated)
```

**For detailed instructions**, see [INSTALLATION.md - Adding Questions](INSTALLATION.md#post-installation-adding-questions).

---

## Utility Scripts

The bot includes several utility scripts for management:

```bash
# Seed topics from config
python scripts/seed_topics.py

# Generate questions (requires API key)
python scripts/generate_questions.py --count 10

# Check database health
python scripts/diagnose_database.py

# Automated setup (Linux/Mac)
bash scripts/setup.sh
```

**For detailed documentation**, see [scripts/README.md](scripts/README.md).

---

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src

# Validate examples manually
python scripts/validate_examples.py

# Diagnose database and topics
python scripts/diagnose_database.py
```

### Troubleshooting

**Bot can't see topics:**

1. Run the diagnostic tool:
   ```bash
   python scripts/diagnose_database.py
   ```

2. Check database path:
   - Make sure you're running the bot from the project root directory
   - SQLite paths are relative to the current working directory
   - Default: `sqlite:///./learning_bot.db` → `./learning_bot.db`

3. Verify topics are seeded:
   ```bash
   python scripts/seed_topics.py
   ```

4. Check the logs when starting the bot:
   - Look for "Database absolute path" in startup logs
   - Look for "found X topics in database" message

**No questions available:**

- Questions are generated automatically if `ENABLE_SCHEDULER=true`
- Or manually run question generation (see Phase 4 docs)
- Topics will still be visible even without questions

## Project Structure

```
learn-telegram-bot/
├── src/
│   ├── core/           # Startup and initialization
│   ├── handlers/       # Telegram bot handlers
│   ├── services/       # LLM, scheduling, analytics
│   ├── database/       # SQLAlchemy models
│   └── utils/          # Configuration, logging, exceptions
├── config/
│   ├── topics.yaml
│   ├── prompts.yaml
│   ├── difficulty_levels.yaml
│   └── examples/       # Example question files
├── deployment/         # Production deployment configs
│   ├── telegram-learning-bot.service  # systemd (Linux)
│   ├── com.user.telegram-learning-bot.plist  # launchd (macOS)
│   └── README.md       # Deployment guide
├── scripts/            # Utility scripts
│   ├── setup.sh        # Automated setup
│   ├── seed_topics.py  # Database seeding
│   └── diagnose_database.py  # Health check
├── Dockerfile          # Docker container config
├── docker-compose.yml  # Docker orchestration
└── docs/               # Documentation
```

## Development

### Coding Standards

This project follows the guidelines in `AI.md`:
- PEP8 style guide
- Type hints for all functions
- Google-style docstrings
- Modular design (< 800 lines per file)
- Comprehensive error handling
- Pytest for testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_validator.py
```

## Contributing

1. Follow the coding standards in `AI.md`
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

## License

[Add your license here]

## Acknowledgments

- Powered by [OpenRouter](https://openrouter.ai/)
- Built with [python-telegram-bot](https://python-telegram-bot.org/)
