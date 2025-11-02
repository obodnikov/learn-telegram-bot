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
- 🎲 **Randomized Selection**: Questions selected randomly with mastery-based exclusion
- 📝 **Example-Based Learning**: Configure question style using example files
- 🔄 **Smart Duplicate Prevention**: Automatically tracks used examples and prevents duplicate questions
- 🌍 **Multilingual**: Support for any language pair (e.g., Hungarian/Russian)
- 📊 **Interactive Statistics**: Comprehensive learning analytics with per-topic drill-down
- ⚙️ **Highly Configurable**: YAML-based topic and prompt configuration
- 🛠️ **Topic Management**: CLI tools for syncing, updating, and managing topics

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
- [x] Smart duplicate detection and prevention
- [x] Example question tracking (hybrid mode optimization)

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

The bot provides a convenient commands menu accessible via the menu button in Telegram:

- `/start` - Register and welcome message
- `/help` - Show available commands
- `/topics` - List topics and start quiz (requires questions!)
- `/stats` - View learning statistics
- `/cancel` - End current quiz session

The commands menu is automatically set up when the bot starts, making it easy for users to discover and use available commands.

### Learning Statistics

The `/stats` command provides comprehensive learning analytics:

**Interactive Menu:**
- Overall statistics across all topics
- Tap topic buttons to view detailed per-topic stats
- Visual progress bars and mastery percentages

**Metrics Tracked:**
- Total questions, seen, and not yet seen
- Correct/incorrect answers and accuracy
- Questions known (mastered with 2+ consecutive correct)
- Questions currently learning
- Questions due for review (spaced repetition)
- Average response time
- Last activity timestamp

**Example**: Type `/stats` → tap "Hungarian Vocabulary - Beginner" → see detailed progress with visual indicators.

**For complete documentation**, see [STATS_FEATURE.md](STATS_FEATURE.md).

---

## Question Generation

**Status After Installation**: 0 questions in database

The bot can show topics but **cannot start quizzes** without questions!

### Manual Generation (Recommended)

Generate questions on-demand using the CLI script with standard or enhanced mode:

**Standard Generation:**
```bash
# Generate 10 questions per topic
python scripts/generate_questions.py --count 10

# Generate for specific topic
python scripts/generate_questions.py --topic 1 --count 15

# Use defaults (5 per topic)
python scripts/generate_questions.py
```

**Enhanced Generation (with Duplicate Detection):**
```bash
# Use fuzzy duplicate detection with retry logic
python scripts/generate_questions.py --enhanced --count 10

# Fine-tune duplicate detection
python scripts/generate_questions.py --enhanced \
  --similarity-threshold 0.90 \
  --duplicate-retry-threshold 0.40 \
  --max-retries 5

# Generate many questions with higher token limit
python scripts/generate_questions.py --count 20 --max-output-tokens 8000
```

**Requirements**:
- OpenRouter API key (get at https://openrouter.ai/keys)
- Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-your-key`
- ~$0.02-0.05 per 10 questions

**For detailed usage examples and explanations**, see [GENERATE_QUESTIONS.md](GENERATE_QUESTIONS.md).

### Automatic Generation (Scheduler)

Enable continuous generation in `.env`:

```env
ENABLE_SCHEDULER=true
OPENROUTER_API_KEY=sk-or-v1-your-key
QUESTION_GENERATION_SCHEDULE=0 */3 * * *  # Every 3 hours
QUESTIONS_PER_RUN=5  # 5 per topic
```

Then restart the bot. Questions will generate automatically on schedule.

**Cost estimate**: ~$0.05-0.10 per day with default settings.

### Verify Questions

```bash
# Check how many questions you have
python scripts/diagnose_database.py

# Should show:
#   Total questions: 20 (or whatever you generated)
```

**For detailed generation guide with examples**, see [GENERATE_QUESTIONS.md](GENERATE_QUESTIONS.md).

### Smart Question Management

The bot intelligently manages questions to prevent duplicates:

**Duplicate Prevention**:
- ✅ Automatically tracks which example questions are already in the database
- ✅ Only uses unused examples from your example files
- ✅ Checks generated questions against existing ones before saving
- ✅ Seamlessly transitions to pure generation when examples are exhausted

**How it works**:
```bash
# First run: Uses 2 examples + generates 3 new (total: 5)
python scripts/generate_questions.py --topic 1 --count 5
# Output: "Filtered examples: 6 total, 6 unused, 0 already in database"
# Output: "Hybrid mode: selected 2 from file, will generate 3 new questions"

# After multiple runs: All examples used, generates all new
python scripts/generate_questions.py --topic 1 --count 5
# Output: "Filtered examples: 6 total, 0 unused, 6 already in database"
# Output: "Hybrid mode: no unused examples available, will generate all questions"
```

This means you can safely run generation multiple times without worrying about duplicates!

---

## Topic Management

After initial setup, you can manage topics using CLI tools. Topics are defined in `config/topics.yaml` and synced to the database.

### Managing Topics with CLI

**View all topics:**
```bash
python scripts/manage_topics.py list
```

**Sync YAML changes to database:**
```bash
# Preview changes (dry-run)
python scripts/manage_topics.py sync --dry-run

# Apply changes
python scripts/manage_topics.py sync

# Or use convenience script
python scripts/sync_topics.py
```

**Show differences between YAML and database:**
```bash
python scripts/manage_topics.py diff
```

**Deactivate/Activate topics:**
```bash
# Soft delete (set is_active=False)
python scripts/manage_topics.py delete <topic_id>

# Reactivate
python scripts/manage_topics.py activate <topic_id>
```

**Export database to YAML:**
```bash
# Export with timestamp filename
python scripts/manage_topics.py export

# Export to specific file
python scripts/manage_topics.py export --output backup.yaml

# Or use convenience script
python scripts/export_topics.py topics_backup.yaml
```

### Topic Management Workflow

**Adding new topics:**
1. Add topic definition to `config/topics.yaml`
2. Run `python scripts/sync_topics.py --dry-run` to preview
3. Run `python scripts/sync_topics.py` to apply
4. Generate questions: `python scripts/generate_questions.py --count 10`

**Updating topic parameters:**
1. Edit topic in `config/topics.yaml` (e.g., change difficulty, questions_per_batch)
2. Run `python scripts/sync_topics.py` to update database
3. Changes apply immediately to new quiz sessions

**Removing topics:**
1. Remove topic from `config/topics.yaml`
2. Run `python scripts/sync_topics.py`
3. Topic is soft-deleted (set to inactive) - questions preserved

**For detailed documentation**, see [scripts/README.md - Topic Management](scripts/README.md#topic-management).

---

## Quiz Behavior

### Session Management

Quiz sessions respect the `questions_per_batch` parameter from topic configuration:

```yaml
# config/topics.yaml
topics:
  hungarian_vocabulary_beginner:
    questions_per_batch: 10  # Session ends after 10 questions
```

When the batch limit is reached, the bot displays session statistics and ends the quiz.

### Intelligent Question Selection

Questions are selected using a hybrid algorithm that balances new content exposure with spaced repetition:

**Configurable Unseen Ratio:**
- By default, 40% of questions in each session are **unseen** (new) questions
- The remaining 60% follow spaced repetition priority
- Configurable via `UNSEEN_QUESTIONS_RATIO` in `.env` (e.g., `0.40` = 40%)

**Selection Logic:**
1. **Unseen Questions (40% quota)**:
   - If unseen quota not met → select random unseen question
   - Ensures steady introduction of new material

2. **Spaced Repetition (60% or when quota met)**:
   - **Priority 1**: Due for review (`next_review_at <= now`, not mastered) - random
   - **Priority 2**: Not mastered (`consecutive_correct < 2`) - random
   - **Fallback**: Unseen questions (if quota already met)

**Mastery Exclusion:**
- Questions with 2+ consecutive correct answers are "known" (mastered)
- Known questions are automatically excluded from selection
- Focuses learning on material that needs practice

**Benefits:**
- ✅ **Balanced learning**: New content + review in every session
- ✅ **Consistent progress**: Always learn something new (if available)
- ✅ **Spaced repetition**: Reviews prioritized when quota is met
- ✅ **Unpredictable order**: Random selection within each category
- ✅ **Gradual mastery**: Question pool shrinks as knowledge grows

**Example** (10 questions per session, 40% unseen ratio):
- Questions 1-4: Unseen/new questions (40%)
- Questions 5-10: Due for review or other non-mastered (60%)

---

## Utility Scripts

The bot includes several utility scripts for management:

```bash
# Initial setup
python scripts/seed_topics.py              # Seed topics from YAML (first time)
bash scripts/setup.sh                      # Automated setup (Linux/Mac)

# Topic management
python scripts/manage_topics.py list       # List all topics with details
python scripts/sync_topics.py              # Sync YAML changes to database
python scripts/manage_topics.py diff       # Show YAML vs database differences
python scripts/export_topics.py            # Export database to YAML

# Question generation (requires API key)
python scripts/generate_questions.py --count 10     # Generate 10 per topic
python scripts/generate_questions.py --topic 1 --count 15  # Specific topic

# Database management
python scripts/diagnose_database.py        # Check database health and stats
```

**For detailed documentation**, see [scripts/README.md](scripts/README.md).

**Note**: When generating questions, use batches of 10-15 for best results. Larger batches (25+) may fail due to LLM response size limits. To generate many questions, run the script multiple times with smaller counts.

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
