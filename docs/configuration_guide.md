# Configuration Guide

## Overview

This guide explains how to configure the Telegram Learning Bot for your specific learning topics.

## Configuration Files

### 1. Environment Variables (.env)

Create a `.env` file based on `.env.example`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Database Configuration
DATABASE_URL=sqlite:///learning_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Scheduler Configuration
GENERATION_START_HOUR=10
GENERATION_END_HOUR=19
GENERATION_INTERVAL_HOURS=3
QUESTIONS_PER_BATCH=10
```

### 2. Topics Configuration (config/topics.yaml)

Define learning topics:

```yaml
topics:
  topic_id:
    name: "Display Name"
    type: language|history|science
    target_language: "Hungarian"  # For language topics
    native_language: "Russian"     # For language topics
    difficulty: beginner|intermediate|advanced|expert
    questions_per_batch: 10
    context: |
      Detailed context about what to focus on.
      Multiple lines supported.
    
    # Optional: Example file configuration
    examples:
      file: "config/examples/topic_id.json"
      mode: augment|template|hybrid
      use_ratio: 0.4  # For hybrid mode
```

**Topic Types:**
- `language`: Language learning (vocabulary, grammar, phrases)
- `history`: Historical facts, dates, events
- `science`: Scientific concepts and facts

**Example Modes:**
- `augment`: LLM creates new questions similar to examples
- `template`: LLM uses exact structure, changes content
- `hybrid`: Mix provided examples (use_ratio) with generated questions

### 3. Prompts Configuration (config/prompts.yaml)

Customize LLM prompts for question generation. See existing file for structure.

### 4. Difficulty Levels (config/difficulty_levels.yaml)

Defines criteria for each difficulty level. Generally, you don't need to modify this.

## Example Files

### Creating Example Question Files

Example files guide the LLM to generate high-quality questions.

**File location:** `config/examples/{topic_id}.json`

**Structure:**

```json
{
  "meta": {
    "topic": "topic_id",
    "target_language": "Hungarian",
    "native_language": "Russian",
    "difficulty": "intermediate",
    "total_questions": 5,
    "created_by": "human",
    "notes": "Optional notes about the examples"
  },
  "questions": [
    {
      "question": "Question text in native language",
      "choices": {
        "A": "First choice",
        "B": "Second choice",
        "C": "Third choice",
        "D": "Fourth choice"
      },
      "correct": "B",
      "explanation": "Native Language: Explanation...\n\nTarget Language: Translation...",
      "difficulty": "intermediate",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

**Best Practices:**

1. **Quality over Quantity**: 5-10 excellent examples are better than 50 mediocre ones
2. **Diverse Examples**: Cover different question types within the topic
3. **Clear Explanations**: Bilingual explanations for language topics
4. **Plausible Distractors**: Wrong answers should be believable but clearly incorrect
5. **Consistent Difficulty**: All examples should match declared difficulty level
6. **Rich Tags**: Help categorize and track question types

## Adding a New Topic

1. **Create example file** (optional but recommended):
   ```bash
   cp config/examples/hungarian_vocabulary.json config/examples/my_topic.json
   # Edit the file with your examples
   ```

2. **Add topic to topics.yaml**:
   ```yaml
   my_topic:
     name: "My Learning Topic"
     type: language  # or history, science
     target_language: "French"
     native_language: "English"
     difficulty: beginner
     questions_per_batch: 10
     context: |
       What should be covered in this topic.
     examples:
       file: "config/examples/my_topic.json"
       mode: hybrid
       use_ratio: 0.3
   ```

3. **Restart the bot** - it will validate the configuration on startup

## Validation

The bot validates all configurations on startup:

- ✅ YAML syntax
- ✅ Required fields present
- ✅ Valid difficulty levels
- ✅ Example files exist and are valid
- ✅ Topic-example references

Check logs for validation results:
```bash
python main.py
# Look for "All startup checks passed!"
```

## Troubleshooting

### "Topic not found" error
- Check topic_id spelling in topics.yaml
- Ensure proper YAML indentation

### "Example file not found"
- Verify file path in examples.file
- Check file exists in config/examples/

### "Invalid difficulty level"
- Must be one of: beginner, intermediate, advanced, expert
- Check spelling (case-sensitive)

### Validation errors on startup
- Review error messages in logs
- Run manual validation: `python scripts/validate_examples.py`

## Environment-Specific Configuration

### Development
```env
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev.db
```

### Production
```env
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host/db
```

## Security

⚠️ **Never commit .env file to version control!**

- Keep API keys secret
- Use environment variables in production
- Rotate keys periodically
