# API Reference

## Overview

This document provides API documentation for the Telegram Learning Bot's internal components.

---

## Utils Module

### ConfigLoader

**Location:** `src/utils/config_loader.py`

Manages loading and accessing all configuration files.

```python
from src.utils.config_loader import ConfigLoader

loader = ConfigLoader("config")
loader.load_all()

# Get topic configuration
topic = loader.get_topic("hungarian_vocabulary")

# Get prompt template
prompt = loader.get_prompt("language", "augment")
```

**Methods:**

- `load_all()` - Load all configuration files
- `load_topics() -> Dict[str, TopicConfig]` - Load topics.yaml
- `load_prompts() -> Dict[str, Any]` - Load prompts.yaml
- `load_difficulty_levels() -> Dict[str, Any]` - Load difficulty_levels.yaml
- `get_topic(topic_id: str) -> TopicConfig` - Get specific topic
- `get_prompt(topic_type: str, mode: str) -> str` - Get prompt template

### DifficultyManager

**Location:** `src/utils/difficulty.py`

Manages difficulty levels and validation.

```python
from src.utils.difficulty import DifficultyManager, DifficultyLevel

# Validate difficulty
is_valid = DifficultyManager.validate_difficulty("intermediate")

# Get description
desc = DifficultyManager.get_difficulty_description("beginner")

# Suggest difficulty
level = DifficultyManager.suggest_difficulty(2000, "language")
```

**Methods:**

- `validate_difficulty(difficulty: str) -> bool` - Check if valid
- `get_difficulty_description(difficulty: str) -> str` - Get description
- `suggest_difficulty(vocabulary_size: int, topic_type: str) -> DifficultyLevel` - Suggest level

### Logger

**Location:** `src/utils/logger.py`

Centralized logging configuration.

```python
from src.utils.logger import setup_logger, get_logger

# Setup (usually in main.py)
setup_logger(log_level="INFO", log_file="logs/bot.log")

# Get logger in modules
logger = get_logger(__name__)
logger.info("Message")
logger.error("Error message")
```

**Functions:**

- `setup_logger(log_level, log_file, rotation, retention)` - Configure logging
- `get_logger(name: str)` - Get logger instance

### Exceptions

**Location:** `src/utils/exceptions.py`

Custom exception classes.

```python
from src.utils.exceptions import (
    ConfigurationError,
    ValidationError,
    ExampleFileError,
    LLMServiceError,
    DatabaseError,
    QuestionGenerationError
)

# Raise custom exception
raise ConfigurationError("Invalid config")

# Catch specific exception
try:
    validate_file(path)
except ExampleFileError as e:
    print(e.errors)
```

---

## Services Module

### ExampleValidator

**Location:** `src/services/validator.py`

Validates example question files against schema.

```python
from src.services.validator import ExampleValidator

validator = ExampleValidator()

# Validate single file
is_valid, errors = validator.validate_file("config/examples/topic.json")

# Validate all examples
summary = validator.validate_all_examples("config/examples")
```

**Methods:**

- `validate_file(file_path: str) -> Tuple[bool, List[str]]` - Validate one file
- `validate_all_examples(examples_dir: str) -> Dict[str, Any]` - Validate directory
- `_validate_semantics(data: Dict) -> List[str]` - Internal semantic validation

### LLMService

**Location:** `src/services/llm_service.py`

Interface to OpenRouter API for question generation.

```python
from src.services.llm_service import LLMService

llm = LLMService(api_key="your_key", model="anthropic/claude-3.5-sonnet")

# Generate questions
questions = await llm.generate_questions(prompt, temperature=0.7)

# Test connection
is_connected = await llm.test_connection()
```

**Methods:**

- `generate_questions(prompt, temperature, max_tokens) -> List[Dict]` - Generate questions
- `validate_response(response: str) -> List[Dict]` - Validate LLM output
- `test_connection() -> bool` - Test API connection

### QuestionGenerator

**Location:** `src/services/question_generator.py`

Generates questions using LLM with optional examples.

```python
from src.services.question_generator import QuestionGenerator

generator = QuestionGenerator(llm_service, config_loader, example_parser)

# Generate questions for topic
questions = await generator.generate_questions("hungarian_vocabulary", count=10)
```

**Methods:**

- `generate_questions(topic_id: str, count: int) -> List[Dict]` - Main generation method
- `_generate_standard(topic_config, count)` - Generate without examples
- `_generate_augmented(topic_config, examples, count)` - Generate similar to examples
- `_generate_templated(topic_config, examples, count)` - Use example templates
- `_generate_hybrid(topic_config, examples, total_count, use_ratio)` - Mix provided & generated
- `_build_prompt(topic_config, mode, examples, count)` - Build LLM prompt

### ExampleParser

**Location:** `src/services/example_parser.py`

Parses and manages example question files.

```python
from src.services.example_parser import ExampleParser, ExampleQuestion

parser = ExampleParser()

# Load examples
examples = parser.load_examples("config/examples/topic.json")

# Select for hybrid mode
selected, to_generate = parser.select_questions_for_hybrid(
    examples, total_needed=10, use_ratio=0.3
)

# Format for prompt
formatted = parser.format_examples_for_prompt(examples, mode="augment")
```

**Methods:**

- `load_examples(file_path: str) -> List[ExampleQuestion]` - Load from JSON
- `select_questions_for_hybrid(examples, total_needed, use_ratio) -> Tuple` - Select subset
- `format_examples_for_prompt(examples, mode) -> str` - Format for LLM

### QuestionScheduler

**Location:** `src/services/scheduler.py`

Schedules automatic question generation.

```python
from src.services.scheduler import QuestionScheduler

scheduler = QuestionScheduler(
    question_generator,
    repository,
    start_hour=10,
    end_hour=19,
    interval_hours=3
)

scheduler.start()
# ... bot runs ...
scheduler.stop()
```

**Methods:**

- `start()` - Start scheduler
- `stop()` - Stop scheduler
- `generate_questions_for_all_topics()` - Generate for all topics
- `is_within_generation_hours() -> bool` - Check if in allowed time

### AnalyticsService

**Location:** `src/services/analytics_service.py`

Tracks and analyzes question performance.

```python
from src.services.analytics_service import AnalyticsService

analytics = AnalyticsService(repository)

# Update performance
await analytics.update_question_performance(
    question_id=123,
    was_correct=True,
    response_time=15.5
)

# Get quality score
score = await analytics.calculate_quality_score(question_id=123)

# Find low-quality questions
low_quality = await analytics.get_low_quality_questions(threshold=0.4)

# Export best questions
best = await analytics.export_best_questions(
    topic_id=1,
    min_quality_score=0.8,
    output_file="best_questions.json"
)
```

**Methods:**

- `update_question_performance(question_id, was_correct, response_time)` - Update metrics
- `calculate_quality_score(question_id) -> float` - Calculate quality (0-1)
- `get_low_quality_questions(threshold) -> List[int]` - Find questions needing review
- `get_user_learning_curve(user_id, topic_id) -> Dict` - Get learning progress
- `suggest_question_improvements(question_id) -> Dict` - Suggest improvements
- `export_best_questions(topic_id, min_quality_score, output_file) -> List` - Export high-quality

---

## Database Module

### Repository

**Location:** `src/database/repository.py`

Data access layer for all database operations.

```python
from src.database.repository import Repository

repo = Repository(db_url="sqlite:///learning_bot.db")

# User operations
user = await repo.get_user_by_telegram_id(123456789)
new_user = await repo.create_user(telegram_id=123456789, native_language="Russian")

# Topic operations
topics = await repo.get_all_topics(active_only=True)
topic = await repo.get_topic(topic_id=1)

# Question operations
question = await repo.create_question(question_data)
next_q = await repo.get_next_question(user_id=1, topic_id=1)

# Progress operations
await repo.update_progress(user_id=1, question_id=1, is_correct=True, response_time=12.5)

# Analytics operations
stats = await repo.get_user_stats(user_id=1, topic_id=1)
await repo.update_question_analytics(question_id=1)
```

**User Methods:**

- `get_user_by_telegram_id(telegram_id) -> Optional[User]`
- `create_user(telegram_id, native_language) -> User`

**Topic Methods:**

- `get_all_topics(active_only) -> List[Topic]`
- `get_topic(topic_id) -> Optional[Topic]`

**Question Methods:**

- `create_question(question_data) -> Question`
- `get_next_question(user_id, topic_id) -> Optional[Question]`

**Progress Methods:**

- `update_progress(user_id, question_id, is_correct, response_time)`

**Analytics Methods:**

- `get_user_stats(user_id, topic_id) -> dict`
- `update_question_analytics(question_id)`

### Models

**Location:** `src/database/models.py`

Data models and enums.

```python
from src.database.models import (
    User,
    Topic,
    Question,
    UserProgress,
    QuestionAnalytics,
    ExampleFileValidation,
    QuestionSource,
    ValidationStatus
)

# Enums
source = QuestionSource.LLM
status = ValidationStatus.VALID
```

**Models:**

- `User` - User account
- `Topic` - Learning topic
- `Question` - Quiz question
- `UserProgress` - User's progress on questions
- `QuestionAnalytics` - Question performance metrics
- `ExampleFileValidation` - Validation log for example files

**Enums:**

- `QuestionSource` - FILE, LLM, HYBRID
- `ValidationStatus` - VALID, INVALID, WARNING

---

## Core Module

### StartupValidator

**Location:** `src/core/startup.py`

Validates configuration and files on application startup.

```python
from src.core.startup import StartupValidator

validator = StartupValidator("config")

# Run all checks
success = validator.run_startup_checks()

if not success:
    sys.exit(1)
```

**Methods:**

- `run_startup_checks() -> bool` - Run all validations
- `_validate_topic_example_refs()` - Check topic references
- `_check_env_variables()` - Validate environment vars

---

## Bot Module

### LearningBot

**Location:** `src/bot.py`

Main bot class (Phase 3).

```python
from src.bot import LearningBot

bot = LearningBot(token="your_token")
await bot.start()
```

---

## Handlers Module

### Command Handlers

**Location:** `src/handlers/commands.py`

Telegram command handlers (Phase 3).

- `start_command(update, context)` - /start
- `help_command(update, context)` - /help
- `stats_command(update, context)` - /stats

### Quiz Handlers

**Location:** `src/handlers/quiz.py`

Quiz interaction handlers (Phase 3).

- `start_quiz(update, context)` - Start quiz session
- `handle_answer(update, context)` - Process answer
- `show_explanation(update, context)` - Show explanation

### Callback Handlers

**Location:** `src/handlers/callbacks.py`

Button callback handlers (Phase 3).

- `button_callback(update, context)` - Generic button handler
- `topic_selection_callback(update, context)` - Topic selection
- `answer_callback(update, context)` - Answer selection

---

## Scripts

### validate_examples.py

Manually validate all example files.

```bash
python scripts/validate_examples.py
```

### export_best_questions.py

Export high-quality questions (Phase 5).

```bash
python scripts/export_best_questions.py \
  --topic hungarian_vocabulary \
  --min-quality 0.8 \
  --output best_questions.json
```

### run_tests.py

Run all tests and validation.

```bash
python scripts/run_tests.py
```

---

## Type Hints

All functions use type hints for better IDE support:

```python
def load_examples(self, file_path: str) -> List[ExampleQuestion]:
    """Type hints help with autocomplete and error checking."""
    pass

async def generate_questions(
    self,
    topic_id: str,
    count: int
) -> List[Dict[str, Any]]:
    """Async functions use async/await pattern."""
    pass
```

---

## Error Handling

Use custom exceptions for better error messages:

```python
try:
    topic = config_loader.get_topic("invalid_topic")
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Testing

All modules have corresponding test files in `tests/`:

- `test_config_loader.py` - Test configuration loading
- `test_validator.py` - Test example validation
- `test_difficulty.py` - Test difficulty management

Run tests:
```bash
pytest tests/ -v
```

---

## Logging

All modules use centralized logging:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug info")
logger.info("General info")
logger.warning("Warning message")
logger.error("Error occurred")
```

Configure log level in `.env`:
```env
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```
