# Telegram Learning Bot

An intelligent Telegram bot for learning foreign languages, historical facts, and other educational topics using LLM-powered question generation with spaced repetition.

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

```bash
# Clone the repository
git clone <repository-url>
cd learn-telegram-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens
```

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

### Running the Bot

```bash
# First time: Seed topics into database
python scripts/seed_topics.py

# Set environment variables (or use .env file)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export DATABASE_URL="sqlite:///learning_bot.db"
export OPENROUTER_API_KEY="your_api_key"  # Required for question generation

# Optional: Enable automatic question generation (Phase 4)
export ENABLE_SCHEDULER="true"
export QUESTION_GENERATION_SCHEDULE="0 */3 * * *"  # Every 3 hours
export QUESTIONS_PER_RUN="5"

# Run the bot
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
- `/topics` - List topics and start quiz
- `/stats` - View learning statistics
- `/cancel` - End current quiz session

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
├── tests/              # Test suite
├── docs/               # Documentation
└── scripts/            # Utility scripts
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
