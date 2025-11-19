# Topic Reset Feature

## Overview

The Topic Reset feature allows users to restart a completed topic from the beginning while preserving their completion history. This enables users to practice topics multiple times and track their improvement over successive attempts.

## Features

### 1. Reset Button in Topic Statistics
- **Location**: Topic stats view (`/stats` → Select topic)
- **Visibility**: Button appears only when topic is fully finished (all questions mastered)
- **Label**: "🔄 Reset Progress"

### 2. Two-Step Confirmation Process
Users must confirm before resetting to prevent accidental data loss:

1. **Confirmation Screen**: Shows current progress stats that will be archived
2. **Final Confirmation**: "✅ Yes, Reset" or "❌ Cancel" buttons

### 3. Progress History Tracking
- All completions are archived before reset
- History includes:
  - Attempt number (1st, 2nd, 3rd, etc.)
  - Accuracy percentage
  - Questions known/total
  - Completion date
- History is displayed in topic stats (last 3 attempts shown)

### 4. Safety Checks
- ✅ Only finished topics can be reset (all questions with `consecutive_correct >= 2`)
- ✅ Confirmation required before reset
- ✅ Progress automatically archived before deletion
- ✅ History preserved even after reset

## User Flow

```
1. User completes all questions in a topic (masters all questions)
2. User opens /stats and selects the topic
3. Bot shows topic stats with "🔄 Reset Progress" button
4. User clicks "🔄 Reset Progress"
5. Bot shows confirmation with current stats
6. User clicks "✅ Yes, Reset"
7. Bot archives current progress to history
8. Bot clears all progress for the topic
9. User can start the topic fresh via /topics
```

## Example Screenshots (Text Format)

### Topic Stats (Finished Topic)
```
📊 Hungarian Vocabulary - Everyday Life
========================================

*Question Progress:*
📚 Total Questions: 25
👁 Questions Seen: 25
🆕 Not Yet Seen: 0

*Performance:*
✅ Correct: 50
❌ Incorrect: 0
🎯 Accuracy: 100.0%

*Learning Status:*
⭐ Known: 25
📖 Learning: 0
⏰ Due for Review: 0

*Overall Progress:*
📈 Mastery Level: 100.0%
██████████ 100%

*Previous Completions:*
  #1: 100.0% (25/25 known) - 2025-11-19

[🔄 Reset Progress]
[« Back to All Stats]
```

### Reset Confirmation
```
⚠️ Reset Topic: Hungarian Vocabulary - Everyday Life?

Your current progress will be archived:
• Accuracy: 100.0%
• Questions Known: 25/25
• Correct Answers: 50

After reset, you'll start this topic from the beginning.
Your history will be preserved and visible in statistics.

Are you sure you want to continue?

[✅ Yes, Reset]
[❌ Cancel]
```

### Reset Complete
```
✅ Topic Reset Complete!

Topic: Hungarian Vocabulary - Everyday Life
Progress archived as Attempt #1
• Accuracy: 100.0%
• Known Questions: 25/25
• Date: 2025-11-19 09:10

You can now start this topic fresh!
Use /topics to begin learning again.

[« Back to Stats]
```

## Implementation Details

### Database Schema

**New Table: `topic_history`**
```sql
CREATE TABLE topic_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    completion_date DATETIME NOT NULL,
    questions_total INTEGER NOT NULL,
    questions_correct INTEGER NOT NULL,
    questions_incorrect INTEGER NOT NULL,
    accuracy_percentage FLOAT NOT NULL,
    questions_known INTEGER NOT NULL,
    attempt_number INTEGER NOT NULL,
    FOREIGN KEY(topic_id) REFERENCES topics (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
```

**Indexes:**
- `idx_user_topic_history` on `(user_id, topic_id)`
- `ix_topic_history_topic_id` on `topic_id`
- `ix_topic_history_user_id` on `user_id`

### New Repository Methods

#### `is_topic_finished(user_id: int, topic_id: int) -> bool`
Checks if all questions in a topic are mastered (`consecutive_correct >= 2`).

#### `get_topic_history(user_id: int, topic_id: Optional[int]) -> List[TopicHistory]`
Retrieves completion history, ordered by date (newest first).

#### `archive_topic_progress(user_id: int, topic_id: int) -> TopicHistory`
Saves current progress to history before reset. Auto-increments attempt number.

#### `reset_topic_progress(user_id: int, topic_id: int) -> int`
Deletes all user progress for the topic's questions. Returns number of records deleted.

**Raises:** `DatabaseError` if topic is not finished.

### New Callback Handlers

#### `reset_confirm_callback`
- Pattern: `^reset_confirm:`
- Shows confirmation dialog with current stats

#### `reset_execute_callback`
- Pattern: `^reset_execute:`
- Executes archive and reset operations
- Shows success message with archived attempt details

## Files Modified

1. **[src/database/models.py](../src/database/models.py:177-199)** - Added `TopicHistory` model
2. **[src/database/repository.py](../src/database/repository.py:898-1050)** - Added 4 new methods
3. **[src/handlers/callbacks.py](../src/handlers/callbacks.py:327-548)** - Added reset UI logic and handlers
4. **[src/bot.py](../src/bot.py:96-141)** - Registered new callback handlers
5. **[alembic/versions/20251119_0908_c9de22860740_add_topic_history_table.py](../alembic/versions/20251119_0908_c9de22860740_add_topic_history_table.py)** - Database migration

## Testing

### Test Scripts Created

1. **[test_reset_feature.py](../test_reset_feature.py)** - Automated tests for all reset functionality
2. **[simulate_finished_topic.py](../simulate_finished_topic.py)** - Helper script to mark topic as finished

### Running Tests

```bash
# Apply database migration
./venv/bin/alembic upgrade head

# Simulate a finished topic (for testing)
./venv/bin/python simulate_finished_topic.py

# Run reset feature tests
./venv/bin/python test_reset_feature.py
```

### Test Results

✅ All tests passed:
- Topic finish detection works correctly
- History retrieval works correctly
- Archive creates proper history records with incremented attempt numbers
- Reset clears all progress successfully
- Error handling prevents reset of non-finished topics
- Multiple resets create separate history entries

## Migration Instructions

To apply this feature to an existing database:

```bash
# Navigate to project root
cd /path/to/learn-telegram-bot

# Apply migration
./venv/bin/alembic upgrade head

# Verify migration
./venv/bin/alembic current
# Should show: c9de22860740 (head)
```

## Usage Examples

### For Users

1. **Complete a topic** - Answer all questions correctly at least twice (master them)
2. **View stats** - Use `/stats` command and select the topic
3. **Reset topic** - Click "🔄 Reset Progress" button
4. **Confirm reset** - Click "✅ Yes, Reset"
5. **Start fresh** - Use `/topics` to begin the topic again

### For Administrators

Check topic history in database:
```bash
sqlite3 learning_bot.db "SELECT * FROM topic_history;"
```

View specific user's history:
```bash
sqlite3 learning_bot.db "SELECT attempt_number, accuracy_percentage,
questions_known, datetime(completion_date) FROM topic_history
WHERE user_id = 1 AND topic_id = 1 ORDER BY completion_date;"
```

## Future Enhancements

Potential improvements for future versions:

1. **Export history** - Allow users to export their completion history
2. **Achievements** - Award badges for multiple completions or improvement
3. **Comparison view** - Show progress comparison between attempts
4. **Partial reset** - Allow resetting only certain difficulty levels
5. **Time tracking** - Record total time spent per attempt
6. **Best score highlighting** - Mark personal best attempt in history

## Technical Notes

### Performance
- Reset operation uses batch delete for efficiency
- History queries are indexed on `(user_id, topic_id)` for fast lookup
- Maximum 3 history entries shown in UI to prevent clutter

### Data Integrity
- Foreign keys ensure referential integrity
- Transaction-based operations prevent partial resets
- Archive happens before delete to prevent data loss

### Logging
All operations are logged with INFO level:
- Archive: "Archived topic X progress for user Y: attempt Z, accuracy A%"
- Reset: "Reset topic X progress for user Y: deleted Z progress records"

## Support

For issues or questions:
- Check [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- Review test scripts for usage examples
- Examine repository method docstrings

---

**Feature implemented:** 2025-11-19
**Version:** 1.0
**Migration:** c9de22860740
