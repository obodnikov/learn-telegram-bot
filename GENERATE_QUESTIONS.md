# Question Generation Guide

Complete guide to generating questions for the Telegram Learning Bot, including standard and enhanced modes with duplicate detection.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Standard Generation](#standard-generation)
- [Enhanced Generation (Duplicate Detection)](#enhanced-generation-duplicate-detection)
- [Advanced Parameters](#advanced-parameters)
- [Token Management](#token-management)
- [Generation Modes](#generation-modes)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Cost Estimation](#cost-estimation)

---

## Overview

The bot uses OpenRouter API with LLM models (default: Claude 3.5 Sonnet) to generate questions based on your topic configurations. Questions can be generated in two modes:

1. **Standard Mode**: Direct generation, fast and simple
2. **Enhanced Mode**: Fuzzy duplicate detection with retry logic

---

## Prerequisites

### 1. API Key Setup

Get an OpenRouter API key at [https://openrouter.ai/keys](https://openrouter.ai/keys)

Add to your `.env` file:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # Optional, this is default
```

### 2. Topic Configuration

Ensure topics are configured in `config/topics.yaml` and seeded to database:

```bash
# Check topics
python scripts/manage_topics.py list

# If needed, seed/sync topics
python scripts/seed_topics.py
# OR
python scripts/sync_topics.py
```

### 3. Verify Setup

```bash
# Check database status
python scripts/diagnose_database.py
```

---

## Basic Usage

### Generate for All Topics

```bash
# Generate 5 questions per topic (default)
python scripts/generate_questions.py

# Generate 10 questions per topic
python scripts/generate_questions.py --count 10
```

### Generate for Specific Topic

```bash
# Get topic IDs
python scripts/manage_topics.py list

# Generate 15 questions for topic ID 1
python scripts/generate_questions.py --topic 1 --count 15
```

---

## Standard Generation

Standard mode generates questions directly without duplicate checking. Fast and suitable for initial question population.

### Examples

**Generate 10 questions per topic:**
```bash
python scripts/generate_questions.py --count 10
```

**Generate for specific topic:**
```bash
python scripts/generate_questions.py --topic 1 --count 20
```

**Use custom token limit:**
```bash
python scripts/generate_questions.py --count 15 --max-output-tokens 6000
```

### Output Example

```
============================================================
MANUAL QUESTION GENERATION
============================================================
Connected to database: sqlite:///./learning_bot.db
Available topics in database:
  - ID 1: Hungarian Vocabulary - Beginner
  - ID 2: Russian Grammar Basics

Loaded configuration from: config
Using LLM model: anthropic/claude-3.5-sonnet
Max output tokens: 4000

Generating 10 questions per topic (all 2 active topics)
Using STANDARD generation (add --enhanced for duplicate detection)

Starting generation... (this may take 30-60 seconds per topic)

Generating questions for: Hungarian Vocabulary - Beginner
✓ Saved 10 questions for Hungarian Vocabulary - Beginner

Generating questions for: Russian Grammar Basics
✓ Saved 10 questions for Russian Grammar Basics

============================================================
✓ Generation complete!
✓ Total questions generated: 20
============================================================

Next steps:
1. Run diagnostics: python scripts/diagnose_database.py
2. Start/restart your bot: python main.py
3. Test in Telegram: Send /topics and select a topic
```

---

## Enhanced Generation (Duplicate Detection)

Enhanced mode uses fuzzy string matching to detect similar questions and retries generation if too many duplicates are found.

### How It Works

1. **Generate questions** using LLM
2. **Check duplicates** using fuzzy matching (SequenceMatcher)
3. **Calculate duplicate rate** (duplicates / total generated)
4. **Retry if needed** with anti-duplicate prompting
5. **Return unique questions** only

### Basic Enhanced Generation

```bash
# Use enhanced mode with defaults
python scripts/generate_questions.py --enhanced --count 10
```

**Default parameters:**
- Similarity threshold: `0.85` (85% similarity = duplicate)
- Duplicate retry threshold: `0.50` (retry if >50% are duplicates)
- Max retries: `3`
- Recent context: `20` questions shown to LLM

### Fine-Tuning Duplicate Detection

**Stricter duplicate detection (90% similarity):**
```bash
python scripts/generate_questions.py --enhanced \
  --similarity-threshold 0.90 \
  --count 10
```

**Retry more aggressively (retry if >40% duplicates):**
```bash
python scripts/generate_questions.py --enhanced \
  --duplicate-retry-threshold 0.40 \
  --max-retries 5 \
  --count 10
```

**More context for LLM (50 recent questions):**
```bash
python scripts/generate_questions.py --enhanced \
  --recent-context 50 \
  --count 10
```

**Full customization:**
```bash
python scripts/generate_questions.py --enhanced \
  --topic 1 \
  --count 20 \
  --similarity-threshold 0.88 \
  --duplicate-retry-threshold 0.45 \
  --max-retries 4 \
  --recent-context 30 \
  --max-output-tokens 8000
```

### Output Example (Enhanced Mode)

```
============================================================
MANUAL QUESTION GENERATION
============================================================
Connected to database: sqlite:///./learning_bot.db
Available topics in database:
  - ID 1: Hungarian Vocabulary - Beginner

Loaded configuration from: config
Using LLM model: anthropic/claude-3.5-sonnet
Max output tokens: 4000

Generating 10 questions for topic ID 1: Hungarian Vocabulary - Beginner
Using ENHANCED generation with duplicate detection:
  - Similarity threshold: 0.85
  - Duplicate retry threshold: 0.50%
  - Max retries: 3
  - Recent context size: 20

Starting generation... (this may take 30-60 seconds per topic)

Generating questions for: Hungarian Vocabulary - Beginner
INFO: Checking 10 generated questions against 45 existing questions
INFO: Found 6 duplicates (similarity > 0.85), 4 unique
WARNING: Duplicate rate (60.0%) exceeds threshold
INFO: Retry attempt 1/3
INFO: Providing 20 recent questions as anti-duplicate context
INFO: Checking 6 generated questions against 45 existing questions
INFO: Found 1 duplicate (similarity > 0.85), 5 unique
INFO: Duplicate rate (16.7%) acceptable, stopping retry
✓ Saved 9 questions for Hungarian Vocabulary - Beginner

============================================================
✓ Generation complete!
✓ Total questions generated: 9
============================================================
```

---

## Advanced Parameters

### All Available Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--count` | int | 5 | Questions per topic (1-50) |
| `--topic` | int | None | Specific topic ID (None = all topics) |
| `--enhanced` | flag | False | Enable duplicate detection |
| `--similarity-threshold` | float | 0.85 | Duplicate if similarity > threshold (0.0-1.0) |
| `--duplicate-retry-threshold` | float | 0.50 | Retry if duplicate rate > threshold (0.0-1.0) |
| `--max-retries` | int | 3 | Max retry attempts (0-10) |
| `--recent-context` | int | 20 | Recent questions for LLM context (0-100) |
| `--max-output-tokens` | int | 4000 | LLM output token limit (1000-16000) |

### Parameter Tuning Guide

**Similarity Threshold (`--similarity-threshold`)**
- `0.75`: Loose matching, catches very similar questions
- `0.85`: **Recommended**, good balance
- `0.95`: Strict matching, only near-identical questions

**Duplicate Retry Threshold (`--duplicate-retry-threshold`)**
- `0.30`: Very aggressive, retry if 30%+ duplicates
- `0.50`: **Recommended**, retry if 50%+ duplicates
- `0.70`: Lenient, only retry if 70%+ duplicates

**Max Retries (`--max-retries`)**
- `0`: No retries, accept all duplicates
- `3`: **Recommended**, reasonable attempts
- `5`: Persistent, try harder to avoid duplicates

**Recent Context (`--recent-context`)**
- `10`: Small context, faster but less effective
- `20`: **Recommended**, good balance
- `50`: Large context, better duplicate avoidance but slower

---

## Token Management

### Understanding Token Limits

LLM models have output token limits. Questions consume approximately:
- **250-300 tokens per question** (question + choices + explanation)

**Default limit**: 4000 tokens = ~10-15 questions per request

### Generating Many Questions

To generate 20+ questions, increase the token limit:

```bash
# 20 questions: 20 × 300 = 6000 tokens
python scripts/generate_questions.py --count 20 --max-output-tokens 6000

# 30 questions: 30 × 300 = 9000 tokens
python scripts/generate_questions.py --count 30 --max-output-tokens 9000

# Maximum: 50 questions
python scripts/generate_questions.py --count 50 --max-output-tokens 16000
```

### Token Limit Recommendations

| Question Count | Recommended Tokens |
|----------------|--------------------|
| 5 questions | 2000 tokens |
| 10 questions | 4000 tokens (default) |
| 15 questions | 6000 tokens |
| 20 questions | 8000 tokens |
| 30 questions | 10000 tokens |
| 40 questions | 13000 tokens |
| 50 questions | 16000 tokens (max) |

**Note**: Higher token limits increase API costs proportionally.

---

## Vocabulary Guidance System

**Important**: The bot uses an intelligent **hybrid vocabulary guidance approach** to prevent question repetition and maintain consistent quality across multiple generations.

### How It Works

Instead of using specific word lists (which cause LLMs to reuse the same vocabulary), topics use:

1. **Semantic Categories** - Broad topical areas (e.g., "commitment/dedication-related" instead of "elkötelezett, odaadó")
2. **Quality Calibration** - Example words showing the right complexity level with ✓/✗ markers
3. **Explicit Instructions** - Clear directive to NOT reuse the calibration examples

### Example from `config/topics.yaml`

```yaml
Vocabulary level guidance:
  Generate advanced (C1-C2 level) vocabulary with these characteristics:
  - Abstract concepts requiring contextual understanding
  - Words with nuanced meanings and subtle distinctions
  - Formal register used in academic, professional contexts

  Draw from these semantic categories:
  - Adjectives: commitment/dedication-related, sophistication/refinement
  - Nouns: consequences and outcomes, emphasis and importance
  - Verbs: emphasizing and stressing, questioning and doubting

  QUALITY CALIBRATION (do not reuse these specific words):
  ✓ Good complexity: elkötelezett (committed - nuanced, C1-C2 level)
  ✓ Good complexity: kétségbe vonni (to call into question - idiomatic)
  ✗ Too simple: asztal (table - concrete, A1 level)

  Generate NEW vocabulary at the "Good complexity" level.
  Do not reuse the calibration examples above.
```

### Benefits

✅ **Prevents repetition** - LLM understands principles, doesn't copy words
✅ **Maintains difficulty** - Quality calibration keeps consistent level
✅ **Scalable** - Can generate hundreds of questions without degradation
✅ **Flexible** - LLM has creative freedom within boundaries

**For complete details**, see [VOCABULARY_GUIDANCE.md](VOCABULARY_GUIDANCE.md).

---

## Generation Modes

The bot supports different generation strategies based on topic configuration:

### 1. Standard Mode (No Examples)

**Config:**
```yaml
topics:
  my_topic:
    name: "My Topic"
    # No examples configuration
```

**Behavior**: Pure LLM generation using prompts from `config/prompts.yaml`

### 2. Augment Mode (Learn from Examples)

**Config:**
```yaml
topics:
  my_topic:
    examples:
      file: "my_examples.yaml"
      mode: "augment"
```

**Behavior**: LLM studies examples and generates similar questions

### 3. Template Mode (Follow Example Structure)

**Config:**
```yaml
topics:
  my_topic:
    examples:
      file: "my_examples.yaml"
      mode: "template"
```

**Behavior**: LLM follows exact structure of example questions

### 4. Hybrid Mode (Mix Examples + Generated)

**Config:**
```yaml
topics:
  my_topic:
    examples:
      file: "my_examples.yaml"
      mode: "hybrid"
      use_ratio: 0.3  # 30% from file, 70% generated
```

**Behavior**:
- Uses unused questions from example file (30%)
- Generates remaining questions (70%)
- Automatically tracks which examples were used

**Smart duplicate prevention**: Hybrid mode automatically filters out examples already in the database!

---

## Best Practices

### Initial Setup (Empty Database)

```bash
# Step 1: Generate initial question pool
python scripts/generate_questions.py --count 10

# Step 2: Verify
python scripts/diagnose_database.py

# Step 3: Test in Telegram
python main.py
# Then use /topics in Telegram
```

### Growing Question Pool

```bash
# Use enhanced mode to avoid duplicates
python scripts/generate_questions.py --enhanced --count 10

# For large databases (100+ questions), increase context
python scripts/generate_questions.py --enhanced \
  --recent-context 50 \
  --count 10
```

### Topic-Specific Generation

```bash
# Generate more for a specific topic
python scripts/generate_questions.py --topic 1 --enhanced --count 20
```

### Bulk Generation Strategy

**Bad approach** (may fail):
```bash
# Too many at once, may exceed token limits
python scripts/generate_questions.py --count 50
```

**Good approach** (multiple batches):
```bash
# Generate in smaller batches
python scripts/generate_questions.py --enhanced --count 15
# Wait for completion, then run again
python scripts/generate_questions.py --enhanced --count 15
python scripts/generate_questions.py --enhanced --count 15
```

### Quality Over Quantity

**Recommended workflow:**
1. Generate 10-15 questions per run
2. Test questions in Telegram
3. Review quality and difficulty
4. Adjust prompts in `config/prompts.yaml` if needed
5. Generate more in batches

---

## Troubleshooting

### Issue: "No questions were generated"

**Possible causes:**
1. No API key or invalid key
2. No active topics in database
3. Network/API issues

**Solution:**
```bash
# Check API key
grep OPENROUTER_API_KEY .env

# Check topics
python scripts/manage_topics.py list

# Check database connection
python scripts/diagnose_database.py
```

### Issue: "All generated questions are duplicates"

**Symptoms**: Enhanced mode shows 100% duplicate rate

**Solutions:**
- Increase `--similarity-threshold` (e.g., 0.90 or 0.95)
- Increase `--recent-context` to show more examples
- Check if prompt configuration needs updating
- Consider using different LLM model

### Issue: "Token limit exceeded"

**Error message**: "Response too large" or "Max tokens exceeded"

**Solution:**
```bash
# Reduce question count
python scripts/generate_questions.py --count 10 --max-output-tokens 4000

# OR increase token limit
python scripts/generate_questions.py --count 15 --max-output-tokens 6000
```

### Issue: "Generation takes too long"

**Causes:**
- Enhanced mode with many retries
- Large database with many questions to compare

**Solutions:**
```bash
# Reduce retries
python scripts/generate_questions.py --enhanced --max-retries 2

# Reduce context size
python scripts/generate_questions.py --enhanced --recent-context 10

# Use standard mode for speed
python scripts/generate_questions.py --count 10
```

### Issue: "Questions are too similar to each other"

**Solution**: Use enhanced mode with stricter settings
```bash
python scripts/generate_questions.py --enhanced \
  --similarity-threshold 0.80 \
  --duplicate-retry-threshold 0.30 \
  --max-retries 5
```

---

## Cost Estimation

### Pricing Model

OpenRouter pricing varies by model. For **Claude 3.5 Sonnet**:
- Input: ~$3.00 per 1M tokens
- Output: ~$15.00 per 1M tokens

### Estimated Costs

**Per generation run:**
| Questions | Input Tokens | Output Tokens | Approx Cost |
|-----------|--------------|---------------|-------------|
| 5 questions | ~500 | ~1,500 | $0.02 |
| 10 questions | ~800 | ~3,000 | $0.05 |
| 20 questions | ~1,200 | ~6,000 | $0.09 |
| 50 questions | ~2,000 | ~15,000 | $0.23 |

**Enhanced mode overhead:**
- Adds ~20-30% cost due to retry attempts and context

**Monthly costs (with scheduler):**
- 5 questions per topic, every 3 hours, 2 topics:
  - ~16 runs/day × $0.02 = $0.32/day
  - Monthly: ~$9.60

**Cost-saving tips:**
1. Use standard mode when duplicates aren't a concern
2. Generate in batches when needed, not on schedule
3. Use lower token limits when possible
4. Consider cheaper LLM models for testing

---

## Examples: Real-World Scenarios

### Scenario 1: Starting Fresh

```bash
# You just set up the bot, need initial questions

# Step 1: Check topics
python scripts/manage_topics.py list
# Output: Topic 1: Hungarian Vocabulary

# Step 2: Generate starter questions
python scripts/generate_questions.py --count 10

# Step 3: Verify
python scripts/diagnose_database.py
# Output: 10 questions for Hungarian Vocabulary

# Step 4: Start bot and test
python main.py
```

### Scenario 2: Growing Question Pool

```bash
# You have 50 questions, want to add more without duplicates

# Use enhanced mode
python scripts/generate_questions.py --enhanced \
  --count 15 \
  --similarity-threshold 0.85 \
  --recent-context 30

# Check results
python scripts/diagnose_database.py
```

### Scenario 3: Topic-Specific Expansion

```bash
# Topic 1 has 100 questions, Topic 2 has only 20
# Want to balance them

# Generate only for Topic 2
python scripts/generate_questions.py --topic 2 \
  --enhanced \
  --count 40 \
  --max-output-tokens 12000

# Verify balance
python scripts/diagnose_database.py
```

### Scenario 4: High-Quality Generation

```bash
# You want very unique questions, willing to wait

# Use strict duplicate detection
python scripts/generate_questions.py --enhanced \
  --count 10 \
  --similarity-threshold 0.90 \
  --duplicate-retry-threshold 0.30 \
  --max-retries 5 \
  --recent-context 50
```

### Scenario 5: Bulk Generation (100+ questions)

```bash
# Generate 100 questions efficiently

# Run 5 times in batches
for i in {1..5}; do
  python scripts/generate_questions.py --enhanced \
    --count 20 \
    --max-output-tokens 8000
  echo "Batch $i complete, waiting 10s..."
  sleep 10
done

# Verify total
python scripts/diagnose_database.py
```

---

## Related Documentation

- [README.md](README.md) - Main project documentation
- [scripts/README.md](scripts/README.md) - All script documentation
- [INSTALLATION.md](INSTALLATION.md) - Setup guide
- [config/topics.yaml](config/topics.yaml) - Topic configuration
- [config/prompts.yaml](config/prompts.yaml) - Prompt templates
- [config/examples/](config/examples/) - Example question files

---

## Summary: Quick Reference

**Basic generation:**
```bash
python scripts/generate_questions.py --count 10
```

**Enhanced (recommended for existing database):**
```bash
python scripts/generate_questions.py --enhanced --count 10
```

**Specific topic:**
```bash
python scripts/generate_questions.py --topic 1 --count 15
```

**Large batch with high quality:**
```bash
python scripts/generate_questions.py --enhanced \
  --count 20 \
  --max-output-tokens 8000 \
  --similarity-threshold 0.88
```

**Check results:**
```bash
python scripts/diagnose_database.py
```

---

**Need help?** See [TROUBLESHOOTING.md](BUGFIX_TOPICS.md) or open an issue on GitHub.
