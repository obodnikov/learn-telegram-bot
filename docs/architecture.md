# Project Architecture

## Overview

The Telegram Learning Bot is structured as a modular Python application with clear separation of concerns.

## Directory Structure

```
learn-telegram-bot/
├── src/                    # Source code
│   ├── core/              # Application initialization
│   ├── handlers/          # Telegram bot handlers
│   ├── services/          # Business logic
│   ├── database/          # Data persistence
│   └── utils/             # Utilities
├── config/                # Configuration files
│   ├── topics.yaml        # Topic definitions
│   ├── prompts.yaml       # LLM prompts
│   └── examples/          # Example questions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## Core Components

### Configuration System (`src/utils/config_loader.py`)
- Loads YAML configuration files
- Validates configuration structure
- Provides typed access to configuration data

### Validation System (`src/services/validator.py`)
- Validates example question files
- Checks JSON schema compliance
- Performs semantic validation

### Startup Process (`src/core/startup.py`)
- Runs validation checks on startup
- Verifies environment configuration
- Ensures all dependencies are ready

### Logging (`src/utils/logger.py`)
- Centralized logging configuration
- File and console output
- Log rotation and retention

## Configuration Files

### topics.yaml
Defines learning topics with:
- Language pairs (target/native)
- Difficulty levels
- Context and scope
- Example file references
- Generation modes

### prompts.yaml
Contains LLM prompt templates for:
- Different topic types (language, history)
- Different generation modes (augment, template, hybrid, standard)
- Customizable parameters

### difficulty_levels.yaml
Defines difficulty criteria:
- Beginner, Intermediate, Advanced, Expert
- Language and history-specific criteria
- Distractor complexity guidelines
- Explanation depth requirements

### examples/*.json
Example question files with:
- Metadata (topic, difficulty, languages)
- Question structure
- Answer choices
- Bilingual explanations
- Tags for categorization

## Phase 1 Implementation Status

✅ **Completed:**
- Project structure created
- Configuration system implemented
- Validation system implemented
- Logging infrastructure set up
- Startup validation process
- Example files created (Hungarian/Russian)

⏳ **Next Steps (Phase 2):**
- Database models (SQLAlchemy)
- Repository pattern implementation
- Migrations setup (Alembic)

## Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Type Safety**: Type hints throughout the codebase
3. **Validation First**: Validate all inputs and configurations
4. **Clear Errors**: Descriptive error messages with context
5. **Testability**: Easy to test in isolation
6. **Documentation**: Comprehensive docstrings

## Error Handling

Custom exception hierarchy:
- `BotError`: Base exception
- `ConfigurationError`: Configuration problems
- `ValidationError`: Validation failures
- `ExampleFileError`: Example file issues
- More to be added in future phases

## Testing Strategy

- Unit tests for each component
- Integration tests for workflows
- Validation tests for configuration
- Mock external dependencies (LLM, Telegram)

## Future Architecture

Planned additions:
- Database layer (Phase 2)
- LLM integration (Phase 3)
- Bot handlers (Phase 4)
- Scheduling system (Phase 5)
- Analytics system (Phase 6)
