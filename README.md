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

Currently ready for **Phase 3: Telegram Bot Handlers**

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

See [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) and [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) for details.

### In Progress
- [ ] Phase 3: Telegram bot handlers
- [ ] Phase 4: Question generation & scheduling
- [ ] Phase 5: Analytics and question refinement

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

```bash
# Validate configuration and examples
python main.py

# Run tests
pytest tests/

# Validate examples manually
python scripts/validate_examples.py
```

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
