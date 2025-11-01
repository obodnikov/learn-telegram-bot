# Utility Scripts

This directory contains utility scripts for managing the Telegram Learning Bot.

---

## Scripts Overview

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `seed_topics.py` | Populate database with topics from config | Once / When adding topics |
| `manage_topics.py` | Manage topics (list, sync, delete, activate, export, diff) | As needed |
| `sync_topics.py` | Sync topics from YAML to database | After config changes |
| `export_topics.py` | Export database topics to YAML | For backup / migration |
| `generate_questions.py` | Manually generate questions | As needed |
| `diagnose_database.py` | Check database health and status | Anytime for debugging |
| `setup.sh` | Automated installation (Linux/Mac) | Once |

---

## seed_topics.py

**Purpose**: Seed database with topics from `config/topics.yaml`

**When to use**:
- First time setup
- After adding new topics to config
- To update existing topic configuration

**Usage**:
```bash
python scripts/seed_topics.py
```

**Output**:
```
INFO - Found 2 topics in configuration
INFO - Created new topic: Hungarian Vocabulary - Everyday Life (ID: 1)
INFO - Created new topic: Hungarian Literature and Culture (ID: 2)
INFO - Topic seeding completed successfully!
```

**Notes**:
- Idempotent: Safe to run multiple times
- Updates existing topics if they already exist
- Creates new topics if they don't exist
- Marks topics as active

---

## generate_questions.py

**Purpose**: Manually generate questions for topics using LLM

**When to use**:
- Initial setup (before launching bot)
- To add more questions to specific topics
- When you want controlled question generation
- Testing question quality

**Requirements**:
- `OPENROUTER_API_KEY` in `.env` file
- Topics seeded in database

**Usage**:

### Generate for all topics
```bash
# Generate 5 questions per topic (default)
python scripts/generate_questions.py

# Generate 10 questions per topic
python scripts/generate_questions.py --count 10

# Generate 25 questions per topic
python scripts/generate_questions.py --count 25
```

### Generate for specific topic

**Step 1: See available topics**
```bash
python scripts/generate_questions.py
# Shows: Available topics in database:
#   - ID 1: Hungarian Vocabulary - Everyday Life
#   - ID 2: Hungarian Literature and Culture
```

**Step 2: Generate for specific topic**
```bash
# Generate 15 questions for topic ID 1
python scripts/generate_questions.py --topic 1 --count 15

# Generate 20 questions for topic ID 2
python scripts/generate_questions.py --topic 2 --count 20
```

**Output**:
```
============================================================
MANUAL QUESTION GENERATION
============================================================
INFO - Connected to database: sqlite:///./learning_bot.db
INFO - Available topics in database:
INFO -   - ID 1: Hungarian Vocabulary - Everyday Life
INFO -   - ID 2: Hungarian Literature and Culture

INFO - Loaded configuration from: config
INFO - Using LLM model: anthropic/claude-3.5-sonnet

INFO - Generating 10 questions for topic ID 1: Hungarian Vocabulary - Everyday Life

INFO - Starting generation... (this may take 30-60 seconds per topic)

INFO - Generating 10 questions for topic: Hungarian Vocabulary - Everyday Life
INFO - Saved 10 questions for topic: Hungarian Vocabulary - Everyday Life
INFO -
============================================================
INFO - ✓ Generation complete!
INFO - ✓ Total questions generated: 10
============================================================

INFO - Next steps:
INFO - 1. Run diagnostics: python scripts/diagnose_database.py
INFO - 2. Start/restart your bot: python main.py
INFO - 3. Test in Telegram: Send /topics and select a topic
```

**Options**:
- `--count N` : Number of questions to generate (1-50)
- `--topic ID` : Generate only for specific topic ID
- `--help` : Show help and examples

**Examples**:
```bash
# Generate 5 questions for all topics
python scripts/generate_questions.py

# Generate 10 questions for all topics
python scripts/generate_questions.py --count 10

# Generate 15 questions for topic 1 only
python scripts/generate_questions.py --topic 1 --count 15

# Generate 20 questions for topic 2 only
python scripts/generate_questions.py --topic 2 --count 20
```

**Cost**:
- ~$0.02-0.05 per 10 questions
- Depends on model (default: Claude 3.5 Sonnet)
- See OpenRouter pricing: https://openrouter.ai/models

**Troubleshooting**:

**"OPENROUTER_API_KEY not found"**
```bash
# Add to .env file
nano .env
# Add: OPENROUTER_API_KEY=sk-or-v1-your-key
```

**"No active topics found"**
```bash
# Seed topics first
python scripts/seed_topics.py
```

**"Topic ID X not found"**
```bash
# Run without --topic to see available IDs
python scripts/generate_questions.py
```

**"Failed to parse LLM response" or "Unterminated string"**
```bash
# This happens when generating too many questions at once
# Solution: Use smaller batches (10-15 questions max)
python scripts/generate_questions.py --count 10

# To generate many questions, run multiple times:
python scripts/generate_questions.py --topic 1 --count 10
python scripts/generate_questions.py --topic 1 --count 10
python scripts/generate_questions.py --topic 1 --count 10
# Now you have 30 questions total
```

**Best Practices**:
- ✅ Use batches of 10-15 questions for reliable generation
- ✅ Run multiple times for larger question sets
- ❌ Avoid generating 25+ questions in a single run (may fail)

---

## diagnose_database.py

**Purpose**: Check database health and show current status

**When to use**:
- After seeding topics
- After generating questions
- Troubleshooting issues
- Verifying setup

**Usage**:
```bash
python scripts/diagnose_database.py
```

**Output (Healthy)**:
```
============================================================
DATABASE DIAGNOSTIC TOOL
============================================================

1. Environment Configuration:
   DATABASE_URL: sqlite:///./learning_bot.db

2. File System:
   Relative path: ./learning_bot.db
   Absolute path: /home/user/learn-telegram-bot/learning_bot.db
   File exists: True
   File size: 81920 bytes

3. Database Connection:
   ✓ Connected successfully

4. Topics in Database:
   Total topics: 2
   - [ACTIVE] Hungarian Vocabulary - Everyday Life (ID: 1)
   - [ACTIVE] Hungarian Literature and Culture (ID: 2)

5. Active Topics:
   Count: 2

6. Questions in Database:
   Total questions: 20

============================================================
✅ DIAGNOSIS: Database is healthy!
   2 active topics available
   Bot should work correctly
============================================================
```

**Output (No Topics)**:
```
4. Topics in Database:
   Total topics: 0
   ⚠️  No topics found in database!
   Run: python scripts/seed_topics.py

❌ DIAGNOSIS: No topics in database!
   Run: python scripts/seed_topics.py
```

**Output (No Questions)**:
```
6. Questions in Database:
   Total questions: 0
   ⚠️  No questions generated yet!
   Note: Topics will still be visible even without questions
```

**What it checks**:
1. Environment configuration (DATABASE_URL)
2. Database file existence and size
3. Database connection
4. Number of topics (active and inactive)
5. Number of questions
6. Overall health status

---

## manage_topics.py

**Purpose**: Comprehensive topic management CLI for all topic operations

**When to use**:
- View all topics and their configurations
- Sync topics from YAML to database
- Deactivate/activate topics
- Export database topics to YAML
- Check differences between YAML and database

**Commands**:

### list - Show all topics
```bash
python scripts/manage_topics.py list
```

**Output**:
```
================================================================================
ALL TOPICS IN DATABASE
================================================================================

Topic ID: 1
  Name: Hungarian Vocabulary - Everyday Life
  Type: language
  Status: ACTIVE
  Created: 2025-01-15 10:30:00
  Config:
    questions_per_batch: 10
    difficulty: intermediate
    target_language: Hungarian
    native_language: English
  Questions: 15

Topic ID: 2
  Name: Hungarian Literature and Culture
  Type: language
  Status: INACTIVE
  Created: 2025-01-15 10:30:00
  Config:
    questions_per_batch: 4
    difficulty: intermediate
  Questions: 8

================================================================================
Total topics: 2
Active: 1
Inactive: 1
================================================================================
```

### sync - Sync topics from YAML to database
```bash
# Preview changes without applying
python scripts/manage_topics.py sync --dry-run

# Apply changes
python scripts/manage_topics.py sync
```

**What it does**:
- ✅ **Add** topics that exist in YAML but not in database
- ↻ **Update** topics that exist in both (preserves questions and user progress)
- ✗ **Deactivate** topics that exist in database but not in YAML (soft delete)

**Output**:
```
================================================================================
SYNCING TOPICS FROM YAML TO DATABASE
================================================================================

Adding 1 new topics:
  + Hungarian Grammar Basics

Updating 2 existing topics:
  ↻ Hungarian Vocabulary - Everyday Life (ID: 1)
    Changed fields: questions_per_batch, difficulty
  ↻ Hungarian Literature and Culture (ID: 2)
    Changed fields: target_language

Deactivating 1 removed topics:
  ✗ Old Topic (ID: 3) - setting to inactive

================================================================================
Sync complete - 4 changes made
================================================================================
```

**Notes**:
- **Safe operation**: Never deletes data, only sets `is_active=False`
- **Preserves progress**: All questions and user statistics remain intact
- **Reactivates**: If topic was inactive and appears in YAML, it's reactivated
- **Use `--dry-run`** first to preview changes

### delete - Deactivate a topic (soft delete)
```bash
python scripts/manage_topics.py delete <topic_id>
```

**Example**:
```bash
python scripts/manage_topics.py delete 2
```

**Output**:
```
================================================================================
DEACTIVATING TOPIC ID: 2
================================================================================

Topic to deactivate:
  Name: Hungarian Literature and Culture
  Type: language
  Questions: 8

Note: This will set is_active=False. The topic and its questions will be preserved.
      You can reactivate it later with: python scripts/manage_topics.py activate 2

✓ Topic 'Hungarian Literature and Culture' has been deactivated
================================================================================
```

**What happens**:
- Topic is hidden from `/topics` command in bot
- All questions remain in database
- User progress is preserved
- Can be reactivated later

### activate - Reactivate a deactivated topic
```bash
python scripts/manage_topics.py activate <topic_id>
```

**Example**:
```bash
python scripts/manage_topics.py activate 2
```

**Output**:
```
================================================================================
ACTIVATING TOPIC ID: 2
================================================================================

Topic to activate:
  Name: Hungarian Literature and Culture
  Type: language
  Questions: 8

✓ Topic 'Hungarian Literature and Culture' has been activated
================================================================================
```

### export - Export database topics to YAML
```bash
# Export with timestamp filename
python scripts/manage_topics.py export

# Export to specific file
python scripts/manage_topics.py export --output topics_backup.yaml
```

**Output**:
```
================================================================================
EXPORTING TOPICS TO YAML
================================================================================

✓ Exported 2 topics to: topics_export_20250115_103000.yaml
================================================================================
```

**Use cases**:
- Create backup before making changes
- Migrate topics to another instance
- Generate YAML from manually created topics

### diff - Show differences between YAML and database
```bash
python scripts/manage_topics.py diff
```

**Output**:
```
================================================================================
YAML vs DATABASE DIFF
================================================================================

✓ Topics to ADD (1):
  + Hungarian Grammar Basics

↻ Topics to UPDATE (2):
  ↻ Hungarian Vocabulary - Everyday Life
  ↻ Hungarian Literature and Culture

✗ Topics to DEACTIVATE (1):
  ✗ Old Topic (will be set to inactive)

================================================================================
```

**Use case**: Preview what `sync` will do before running it

---

## sync_topics.py

**Purpose**: Convenience wrapper for syncing topics from YAML to database

**When to use**:
- After editing `config/topics.yaml`
- Adding new topics
- Updating topic parameters

**Usage**:
```bash
# Preview changes
python scripts/sync_topics.py --dry-run

# Apply changes
python scripts/sync_topics.py
```

**This is equivalent to**:
```bash
python scripts/manage_topics.py sync --dry-run
python scripts/manage_topics.py sync
```

---

## export_topics.py

**Purpose**: Convenience wrapper for exporting database topics to YAML

**When to use**:
- Creating backups
- Migrating to another instance
- Documenting current topic configuration

**Usage**:
```bash
# Export with timestamp filename
python scripts/export_topics.py

# Export to specific file
python scripts/export_topics.py topics_backup.yaml
```

**This is equivalent to**:
```bash
python scripts/manage_topics.py export
python scripts/manage_topics.py export --output topics_backup.yaml
```

---

## Topic Management Workflow

### Initial Setup
```bash
# 1. Create topics in YAML
vim config/topics.yaml

# 2. Seed database
python scripts/seed_topics.py

# 3. Verify
python scripts/manage_topics.py list
```

### Adding New Topics
```bash
# 1. Add topic to config/topics.yaml
vim config/topics.yaml

# 2. Preview changes
python scripts/sync_topics.py --dry-run

# 3. Apply changes
python scripts/sync_topics.py

# 4. Generate questions for new topic
python scripts/generate_questions.py --topic <new_topic_id> --count 10
```

### Updating Topic Configuration
```bash
# 1. Edit config/topics.yaml
vim config/topics.yaml

# 2. Preview changes
python scripts/manage_topics.py diff

# 3. Apply changes
python scripts/sync_topics.py
```

### Removing Topics
```bash
# Option 1: Remove from YAML and sync (recommended)
vim config/topics.yaml  # Remove topic entry
python scripts/sync_topics.py  # Topic will be deactivated

# Option 2: Manually deactivate
python scripts/manage_topics.py delete <topic_id>
```

### Backup and Restore
```bash
# Backup current topics
python scripts/export_topics.py topics_backup_$(date +%Y%m%d).yaml

# Restore from backup (replace config/topics.yaml)
cp topics_backup_20250115.yaml config/topics.yaml
python scripts/sync_topics.py
```

---

## setup.sh

**Purpose**: Automated installation for Linux/Mac

**When to use**:
- Fresh installation
- Quick setup

**Usage**:
```bash
bash scripts/setup.sh
```

**What it does**:
1. Creates virtual environment
2. Installs dependencies
3. Creates `.env` file from template
4. Seeds database with topics
5. Runs diagnostics

**Interactive**:
- Prompts for bot token if not configured
- Offers to edit `.env` file

See [INSTALLATION.md](../INSTALLATION.md#quick-setup-automated) for details.

---

## Common Workflows

### Initial Setup

```bash
# 1. Seed topics
python scripts/seed_topics.py

# 2. Check database
python scripts/diagnose_database.py

# 3. Generate initial questions
python scripts/generate_questions.py --count 10

# 4. Verify again
python scripts/diagnose_database.py

# 5. Start bot
python main.py
```

### Add More Questions

```bash
# Add 20 more questions to all topics
python scripts/generate_questions.py --count 20

# Or target specific topic
python scripts/generate_questions.py --topic 1 --count 30
```

### Add New Topic

```bash
# 1. Edit config/topics.yaml (add new topic)

# 2. Seed to database
python scripts/seed_topics.py

# 3. Verify
python scripts/diagnose_database.py

# 4. Generate questions for new topic
python scripts/generate_questions.py --topic 3 --count 20

# 5. Restart bot
```

### Troubleshooting

```bash
# Check database status
python scripts/diagnose_database.py

# Re-seed topics if needed
python scripts/seed_topics.py

# Generate more questions
python scripts/generate_questions.py --count 10
```

---

## Tips

1. **Run diagnostics often**: Use `diagnose_database.py` frequently to verify state

2. **Generate in batches**: Start with 10-20 questions per topic, add more later

3. **Test quality first**: Generate small batch, test quality, then generate more

4. **Cost control**: Use `--topic` to generate for one topic at a time

5. **Backup database**: Copy `learning_bot.db` before large operations

6. **Check logs**: If scripts fail, check `logs/bot.log` for details

---

## Environment Variables

All scripts respect these environment variables from `.env`:

```env
# Database location
DATABASE_URL=sqlite:///./learning_bot.db

# Configuration directory
CONFIG_DIR=config

# LLM settings (for generate_questions.py)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Logging
LOG_LEVEL=INFO
```

---

## Exit Codes

All scripts return proper exit codes:

- `0` = Success
- `1` = Error (check logs for details)

Use in scripts:
```bash
if python scripts/seed_topics.py; then
    echo "Seeding successful"
else
    echo "Seeding failed"
fi
```

---

**For more information**, see:
- [INSTALLATION.md](../INSTALLATION.md) - Complete setup guide
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Production deployment
