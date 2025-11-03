# Question Management Guide

Complete guide to managing questions in the database using the `manage_questions.py` script.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Commands](#commands)
  - [Export Questions](#export-questions)
  - [Import Questions](#import-questions)
  - [Show Question](#show-question)
  - [List Questions](#list-questions)
  - [Delete Question](#delete-question)
  - [Remove Last N Questions](#remove-last-n-questions)
- [Best Practices](#best-practices)
- [Safety Considerations](#safety-considerations)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **manage_questions.py** script provides a comprehensive CLI for managing questions that are already stored in the database. It allows you to:

- **Export** questions to JSON format for backup or sharing
- **Import** questions from JSON files with duplicate detection
- **View** questions in readable format
- **List** questions with filtering options
- **Delete** individual questions by ID
- **Remove** last N questions (useful for cleaning up bad generations)

All destructive operations include confirmation prompts by default, with a `--force` flag to bypass them for automation.

---

## Installation

The script uses the existing project dependencies. No additional installation required.

**Location**: `scripts/manage_questions.py`

**Basic usage**:
```bash
python scripts/manage_questions.py <command> [options]
```

**Get help**:
```bash
python scripts/manage_questions.py --help
python scripts/manage_questions.py <command> --help
```

---

## Commands

### Export Questions

Export questions to JSON format for backup, sharing, or migration.

**Syntax**:
```bash
python scripts/manage_questions.py export [--topic TOPIC_ID] [--output FILE]
```

**Parameters**:
- `--topic TOPIC_ID` (optional): Export only questions from specific topic
- `--output FILE` (optional): Output filename (auto-generated if not specified)

**Auto-generated filename format**:
```
questions_all_20250103_142530.json          # All topics
questions_hungarian_vocabulary_20250103_142530.json  # Specific topic
```

**Output format**:
```json
[
  {
    "question_text": "Что означает венгерское слово 'odaadó'?",
    "choice_a": "преданный",
    "choice_b": "большой",
    "choice_c": "быстрый",
    "choice_d": "старый",
    "correct_answer": "A",
    "explanation": "Russian: 'odaadó' означает 'преданный', 'посвящённый'...\nHungarian: Az 'odaadó' jelenti...",
    "difficulty": "advanced",
    "tags": ["HU→RU", "прилагательные", "абстрактные понятия"]
  }
]
```

**Note**: Export includes only question data, no database metadata (IDs, created dates, etc.).

**Examples**:

```bash
# Export all questions
python scripts/manage_questions.py export

# Export questions from topic 3
python scripts/manage_questions.py export --topic 3

# Export to specific file
python scripts/manage_questions.py export --output backup_2025.json

# Export specific topic to specific file
python scripts/manage_questions.py export --topic 1 --output beginner_backup.json
```

**Use cases**:
- Regular backups before bulk operations
- Sharing question sets between environments
- Manual question review and editing
- Version control of question content

---

### Import Questions

Import questions from JSON files with automatic duplicate detection.

**Syntax**:
```bash
python scripts/manage_questions.py import --file FILE --topic TOPIC_ID [--force]
```

**Parameters**:
- `--file FILE` (required): Path to JSON file containing questions
- `--topic TOPIC_ID` (required): Topic ID to assign imported questions to
- `--force` (optional): Skip confirmation prompt

**Duplicate detection**:
- Matches by `question_text` field
- Uses fuzzy string matching (90% similarity threshold)
- Skips duplicates automatically
- Shows summary of new vs duplicate questions

**Confirmation prompt example**:
```
Found 10 questions in file:
  - 7 new questions to import
  - 3 duplicates (will be skipped)

Import 7 new questions to topic 'Hungarian Vocabulary - Advanced'? (yes/no):
```

**Examples**:

```bash
# Import with confirmation
python scripts/manage_questions.py import --file questions.json --topic 3

# Import without confirmation (automation)
python scripts/manage_questions.py import --file questions.json --topic 3 --force

# Import from backup
python scripts/manage_questions.py import --file backup_2025.json --topic 1
```

**Error handling**:
- Invalid JSON format → error message with line number
- Missing required fields → lists which fields are missing
- Topic ID not found → error with available topic list
- File not found → error with file path

**Use cases**:
- Restoring from backups
- Importing manually created questions
- Migrating questions between databases
- Adding curated question sets

---

### Show Question

Display a single question in readable format with all details.

**Syntax**:
```bash
python scripts/manage_questions.py show --id QUESTION_ID
```

**Parameters**:
- `--id QUESTION_ID` (required): ID of the question to display

**Output format**:
```
════════════════════════════════════════════════════════════════════════════════
Question ID: 42
Topic: Hungarian Vocabulary - Advanced
Difficulty: advanced
Created: 2025-01-03 14:25:30
════════════════════════════════════════════════════════════════════════════════

Question: Что означает венгерское слово 'odaadó'?

A) преданный
B) большой
C) быстрый
D) старый

Correct Answer: A

Explanation:
Russian: 'odaadó' означает 'преданный', 'посвящённый' (кому-то или чему-то).
Это слово C1-C2 уровня, используется для описания глубокой преданности или
посвящённости делу, человеку или идее.

Hungarian: Az 'odaadó' jelenti, hogy valaki teljesen elkötelezett vagy
önzetlenül szenteli magát valaminek vagy valakinek.

Tags: HU→RU, прилагательные, абстрактные понятия
Source: generated
Total Answers: 15
Correct Answers: 12 (80.0%)
════════════════════════════════════════════════════════════════════════════════
```

**Examples**:

```bash
# Show question 42
python scripts/manage_questions.py show --id 42

# Show question 123
python scripts/manage_questions.py show --id 123
```

**Use cases**:
- Reviewing specific questions before deletion
- Checking question content for quality
- Debugging validation issues
- Viewing statistics for specific questions

---

### List Questions

List questions with filtering options in tabular format.

**Syntax**:
```bash
python scripts/manage_questions.py list [--topic TOPIC_ID] [--difficulty LEVEL] [--limit N]
```

**Parameters**:
- `--topic TOPIC_ID` (optional): Filter by topic ID
- `--difficulty LEVEL` (optional): Filter by difficulty level (beginner/intermediate/advanced)
- `--limit N` (optional): Maximum number of questions to display (default: 50)

**Output format**:
```
Found 127 questions:

ID    | Topic                              | Difficulty   | Question Preview
------|------------------------------------|--------------|-----------------------------------------
42    | Hungarian Vocabulary - Advanced    | advanced     | Что означает венгерское слово 'odaadó'?
43    | Hungarian Vocabulary - Advanced    | advanced     | Как по-венгерски сказать 'убедительный'?
44    | Hungarian Vocabulary - Intermediate| intermediate | Что означает 'találkozó'?
...
```

**Examples**:

```bash
# List all questions (first 50)
python scripts/manage_questions.py list

# List all questions from topic 3
python scripts/manage_questions.py list --topic 3

# List all advanced questions
python scripts/manage_questions.py list --difficulty advanced

# List first 100 beginner questions
python scripts/manage_questions.py list --difficulty beginner --limit 100

# List intermediate questions from topic 2
python scripts/manage_questions.py list --topic 2 --difficulty intermediate

# List all questions without limit
python scripts/manage_questions.py list --limit 10000
```

**Use cases**:
- Getting overview of question database
- Finding questions by topic or difficulty
- Identifying questions to delete
- Reviewing recent additions
- Quality control checks

---

### Delete Question

Delete a single question by ID with confirmation.

**Syntax**:
```bash
python scripts/manage_questions.py delete --id QUESTION_ID [--force]
```

**Parameters**:
- `--id QUESTION_ID` (required): ID of the question to delete
- `--force` (optional): Skip confirmation prompt

**Related data deleted automatically**:
- User progress records (answers from users)
- Question analytics (aggregate statistics)

**Confirmation prompt example**:
```
════════════════════════════════════════════════════════════════════════════════
Question ID: 42
Topic: Hungarian Vocabulary - Advanced
Difficulty: advanced
════════════════════════════════════════════════════════════════════════════════

Question: Что означает венгерское слово 'odaadó'?

A) преданный
B) большой
C) быстрый
D) старый

Correct Answer: A

Users who answered this question: 15

This will also delete:
  - 15 user progress records
  - 1 analytics record

Type 'yes' to confirm deletion:
```

**Examples**:

```bash
# Delete with confirmation
python scripts/manage_questions.py delete --id 42

# Delete without confirmation (automation)
python scripts/manage_questions.py delete --id 42 --force

# Delete question that has no user progress
python scripts/manage_questions.py delete --id 123
```

**Safety features**:
- Shows full question text before deletion
- Shows number of users who answered it
- Requires typing 'yes' (not just 'y')
- `--force` flag for automation scripts

**Use cases**:
- Removing low-quality questions
- Fixing validation errors
- Cleaning up test questions
- Correcting content mistakes

---

### Remove Last N Questions

Remove the last N questions inserted into the database, optionally filtered by topic.

**Syntax**:
```bash
python scripts/manage_questions.py remove-last --count N [--topic TOPIC_ID] [--force]
```

**Parameters**:
- `--count N` (required): Number of questions to remove
- `--topic TOPIC_ID` (optional): Remove only from specific topic
- `--force` (optional): Skip confirmation prompt

**Ordering**: Questions are removed by ID descending (most recent first)

**Confirmation prompt example**:
```
Will remove 5 questions:
  ID 45: Что означает венгерское слово 'rendíthetetlen'? (Hungarian Vocabulary - Advanced)
  ID 44: Как по-венгерски сказать 'сложный'? (Hungarian Vocabulary - Advanced)
  ID 43: Что означает 'átszállni'? (Hungarian Vocabulary - Intermediate)
  ID 42: Как по-венгерски сказать 'встреча'? (Hungarian Vocabulary - Intermediate)
  ID 41: Что означает 'étterem'? (Hungarian Vocabulary - Everyday Life)

This will also delete all related user progress and analytics.

Type 'yes' to confirm deletion:
```

**Examples**:

```bash
# Remove last 5 questions from all topics
python scripts/manage_questions.py remove-last --count 5

# Remove last 10 questions from topic 3
python scripts/manage_questions.py remove-last --count 10 --topic 3

# Remove last 20 questions without confirmation
python scripts/manage_questions.py remove-last --count 20 --force

# Remove last question from topic 1 (quick cleanup)
python scripts/manage_questions.py remove-last --count 1 --topic 1
```

**Use cases**:
- Cleaning up bad generation runs
- Removing test questions after validation
- Rolling back recent additions
- Fixing bulk import mistakes

**Safety features**:
- Shows preview of questions to be deleted
- Shows question text and topic for each
- Requires typing 'yes' for confirmation
- `--force` flag for automation

---

## Best Practices

### Regular Backups

Export questions before major operations:

```bash
# Before bulk deletion
python scripts/manage_questions.py export --output backup_before_cleanup.json

# Topic-specific backup before regeneration
python scripts/manage_questions.py export --topic 3 --output advanced_vocab_backup.json
```

### Quality Control Workflow

1. **Generate questions**:
   ```bash
   python scripts/generate_questions.py --enhanced --count 20 --topic 3
   ```

2. **Review new questions**:
   ```bash
   python scripts/manage_questions.py list --topic 3 --limit 20
   ```

3. **Inspect suspicious questions**:
   ```bash
   python scripts/manage_questions.py show --id 42
   ```

4. **Remove bad questions**:
   ```bash
   python scripts/manage_questions.py delete --id 42
   ```

### Import with Validation

Before importing, validate JSON structure:

```bash
# Test import (will show duplicate detection)
python scripts/manage_questions.py import --file new_questions.json --topic 3

# If validation passes, confirm import
# If validation fails, fix JSON and retry
```

### Bulk Cleanup

Remove last N questions from a bad generation:

```bash
# Check what will be removed
python scripts/manage_questions.py list --topic 3 --limit 20

# Remove if needed
python scripts/manage_questions.py remove-last --count 10 --topic 3
```

### Version Control

Keep question exports in version control:

```bash
# Export by topic
python scripts/manage_questions.py export --topic 1 --output config/examples/beginner_v1.json
python scripts/manage_questions.py export --topic 2 --output config/examples/intermediate_v1.json
python scripts/manage_questions.py export --topic 3 --output config/examples/advanced_v1.json

# Commit to git
git add config/examples/*.json
git commit -m "Update example questions"
```

---

## Safety Considerations

### Confirmation Prompts

All destructive operations require confirmation by default:
- **delete**: Shows question details, requires typing 'yes'
- **remove-last**: Shows list of questions, requires typing 'yes'
- **import**: Shows summary, requires typing 'yes'

Use `--force` flag only in automation scripts where you're certain of the operation.

### Related Data Deletion

When deleting questions, related data is automatically removed:
- **UserProgress**: All user answers for this question
- **QuestionAnalytics**: Aggregate statistics

**Warning**: This cannot be undone! Always export before bulk deletions.

### Database Transactions

All operations use database transactions:
- If operation fails, changes are rolled back
- Database remains in consistent state
- Errors are logged with full context

### Backup Strategy

Recommended backup schedule:
- **Before regeneration**: Export affected topic
- **Weekly**: Full database export
- **Before bulk deletion**: Export affected questions
- **After major edits**: Export changed topics

Example backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
python scripts/manage_questions.py export --output "backups/all_${DATE}.json"
python scripts/manage_questions.py export --topic 1 --output "backups/topic1_${DATE}.json"
python scripts/manage_questions.py export --topic 2 --output "backups/topic2_${DATE}.json"
python scripts/manage_questions.py export --topic 3 --output "backups/topic3_${DATE}.json"
```

---

## Troubleshooting

### Import Fails: "Invalid JSON format"

**Problem**: JSON file has syntax errors

**Solution**: Validate JSON structure:
```bash
python -m json.tool questions.json
```

Fix errors shown in output, then retry import.

### Import Fails: "Missing required fields"

**Problem**: JSON questions missing required fields

**Required fields**:
- `question_text`
- `choice_a`, `choice_b`, `choice_c`, `choice_d`
- `correct_answer`
- `explanation`
- `difficulty`
- `tags`

**Solution**: Add missing fields to JSON file, then retry.

### Export Creates Empty File

**Problem**: Topic ID not found or topic has no questions

**Solution**: List all topics and questions:
```bash
# Check topics exist
python scripts/manage_questions.py list

# Try export without --topic filter
python scripts/manage_questions.py export
```

### Delete Fails: "Question not found"

**Problem**: Question ID doesn't exist in database

**Solution**: List questions to find correct ID:
```bash
python scripts/manage_questions.py list --limit 100
```

### "Too many duplicates" on Import

**Problem**: Most questions in import file already exist

**Solution**: This is expected behavior if reimporting. Duplicates are automatically skipped.

To force reimport:
1. Delete existing questions first
2. Then import new file

### Permission Errors

**Problem**: Cannot write export file

**Solution**: Check file path permissions:
```bash
# Use absolute path
python scripts/manage_questions.py export --output /full/path/to/file.json

# Or ensure current directory is writable
ls -la
```

---

## Related Documentation

- [README.md](README.md) - Main project documentation
- [GENERATE_QUESTIONS.md](GENERATE_QUESTIONS.md) - Question generation guide
- [VOCABULARY_GUIDANCE.md](VOCABULARY_GUIDANCE.md) - Vocabulary guidance system
- [scripts/generate_questions.py](scripts/generate_questions.py) - Question generation script

---

## Summary

The **manage_questions.py** script provides comprehensive database management capabilities:

**Export/Import**:
- Export to JSON for backups and sharing
- Import with automatic duplicate detection
- Version control friendly

**Viewing**:
- List with filters (topic, difficulty, limit)
- Show detailed question information
- Statistics and user progress counts

**Deletion**:
- Delete individual questions by ID
- Remove last N questions (cleanup bad generations)
- Automatic related data cleanup
- Safety confirmations with `--force` override

**Best practices**:
- Regular backups before bulk operations
- Quality control workflow with list/show/delete
- Version control question exports
- Validation before import

**Safety features**:
- Confirmation prompts showing full context
- User progress counts before deletion
- Transaction-based operations
- Comprehensive error handling
