# Interactive Statistics Menu Feature

## Overview

The Telegram Learning Bot now includes an interactive statistics menu that provides comprehensive learning analytics on a per-user, per-topic basis. Users can view overall statistics and drill down into detailed stats for each topic they're learning.

## Features

### User-Based Statistics Tracking

All statistics are tracked individually for each user, ensuring privacy and personalized learning insights.

### Overall Statistics

When users type `/stats`, they see a comprehensive overview including:

**Question Progress:**
- 📚 **Total Questions** - Total questions across all topics
- 👁 **Questions Seen** - Questions the user has encountered at least once
- 🆕 **Not Yet Seen** - Questions never encountered

**Performance Metrics:**
- ✅ **Correct** - Total number of correct answers
- ❌ **Incorrect** - Total number of incorrect answers
- 🎯 **Accuracy** - Percentage of correct answers

**Learning Status:**
- ⭐ **Known** - Questions with 2+ consecutive correct answers (mastered)
- 📖 **Learning** - Questions seen but not yet mastered
- ⏰ **Due for Review** - Questions that need review now (spaced repetition)

**Additional Metrics:**
- ⚡ **Avg Response Time** - Average time to answer questions
- 🕐 **Last Activity** - Most recent learning session timestamp

### Per-Topic Detailed Statistics

Users can tap on any topic button to see detailed statistics including:

**Question Progress:**
- Total questions in the topic
- Questions seen vs not yet seen
- Breakdown by learning status

**Performance:**
- Correct/incorrect answer counts
- Accuracy percentage specific to this topic

**Learning Status:**
- Known (mastered) questions count
- Questions currently being learned
- Questions due for review right now

**Progress Visualization:**
- 📈 **Mastery Level** - Percentage of questions mastered
- Visual progress bar showing mastery progress

**Activity:**
- Last time this specific topic was practiced

### Interactive Navigation

- Main stats screen shows overall summary with buttons for each topic
- Tap a topic button to view detailed stats for that topic
- "Back to All Stats" button returns to the main overview
- Topic buttons show quick stats preview: `Topic Name (seen/total)`

## Implementation Details

### Modified Files

1. **[src/database/repository.py](src/database/repository.py)** (lines 488-576)
   - Enhanced `get_user_stats()` method with 11 comprehensive metrics
   - Added `total_questions` count (all questions in database)
   - Added `questions_not_seen` calculation
   - Changed `questions_mastered` to `questions_known` (consecutive_correct >= 2)
   - Added `questions_learning` (seen but not known)
   - Added `questions_due` (needs review now, excludes known)
   - Added `last_activity` timestamp

2. **[src/handlers/commands.py](src/handlers/commands.py)** (lines 131-209)
   - Rewrote `stats_command()` to show interactive menu
   - Added emoji indicators for better readability
   - Created inline keyboard with topic buttons
   - Shows quick preview stats on each button

3. **[src/handlers/callbacks.py](src/handlers/callbacks.py)** (lines 160-308)
   - Added `topic_stats_callback()` - Shows detailed topic statistics
   - Added `stats_back_callback()` - Returns to main stats menu
   - Includes visual progress bar using block characters
   - Calculates and displays mastery percentage

4. **[src/bot.py](src/bot.py)** (lines 94-127)
   - Registered `topic_stats_callback` with pattern `^stats:`
   - Registered `stats_back_callback` with pattern `^stats:back$`
   - Handlers properly ordered to avoid pattern conflicts

### Statistics Metrics Reference

| Metric | Description | Calculation |
|--------|-------------|-------------|
| `total_questions` | Total questions in database | Count of all questions (filtered by topic if specified) |
| `questions_seen` | Questions encountered by user | Count of UserProgress records |
| `questions_not_seen` | Questions never encountered | `total_questions - questions_seen` |
| `total_correct` | Total correct answers | Sum of `times_correct` from UserProgress |
| `total_incorrect` | Total incorrect answers | Sum of `times_incorrect` from UserProgress |
| `accuracy` | Percentage correct | `total_correct / (total_correct + total_incorrect)` |
| `questions_known` | Mastered questions | Count where `consecutive_correct >= 2` |
| `questions_learning` | In-progress questions | `questions_seen - questions_known` |
| `questions_due` | Questions needing review | Count where `next_review_at <= now` and not known |
| `average_response_time` | Avg time to answer | Mean of all `average_response_time` values |
| `last_activity` | Most recent activity | Max `last_shown_at` timestamp |

### Terminology Choices

As requested by the user:
- **"Questions seen"** instead of "asked" or "encountered"
- **"Known"** instead of "mastered" or "completed"

### Database Schema

No database schema changes were required. The feature uses existing fields:
- `UserProgress.times_correct`
- `UserProgress.times_incorrect`
- `UserProgress.consecutive_correct`
- `UserProgress.next_review_at`
- `UserProgress.last_shown_at`
- `UserProgress.average_response_time`

### Callback Data Format

The implementation uses these callback data patterns:
- `stats:<topic_id>` - View detailed stats for a specific topic (e.g., `stats:1`)
- `stats:back` - Return to main stats overview

Pattern matching ensures no conflicts with existing `topic:<id>` callbacks used for quiz topic selection.

## User Experience Flow

1. User types `/stats` command
2. Bot displays overall statistics with emoji indicators
3. Below stats, inline buttons appear for each topic user has practiced
4. Buttons show format: `📘 Topic Name (5/10)` (5 seen out of 10 total)
5. User taps a topic button
6. Bot shows detailed statistics for that topic
7. Visual progress bar shows mastery level
8. "« Back to All Stats" button appears
9. User can tap back to return to overview

## Example Output

### Overall Stats Screen
```
📊 Your Learning Statistics

📚 Total Questions: 30
👁 Questions Seen: 12
🆕 Not Yet Seen: 18

✅ Correct: 15
❌ Incorrect: 5
🎯 Accuracy: 75.0%

⭐ Known: 4
📖 Learning: 8
⏰ Due for Review: 3

⚡ Avg Response Time: 8.5s
🕐 Last Activity: 2025-11-02 10:30

_Tap a topic below for detailed stats:_

[📘 Hungarian Vocabulary - Beginner (6/15)]
[📘 Hungarian Vocabulary - Advanced (6/15)]
```

### Topic Detail Screen
```
📊 Hungarian Vocabulary - Beginner
========================================

Question Progress:
📚 Total Questions: 15
👁 Questions Seen: 6
🆕 Not Yet Seen: 9

Performance:
✅ Correct: 8
❌ Incorrect: 2
🎯 Accuracy: 80.0%

Learning Status:
⭐ Known: 2
📖 Learning: 4
⏰ Due for Review: 1

Speed:
⚡ Avg Response Time: 7.2s

Activity:
🕐 Last Practiced: 2025-11-02 10:15

Overall Progress:
📈 Mastery Level: 13.3%
████░░░░░░ 13%

[« Back to All Stats]
```

## Benefits

1. **Motivation** - Visual progress tracking encourages continued learning
2. **Focus** - "Due for Review" count helps users prioritize what to practice
3. **Insights** - Accuracy and response time metrics show areas for improvement
4. **Organization** - Per-topic breakdown helps manage multiple learning subjects
5. **Spaced Repetition** - "Known" vs "Learning" status aligns with SRS algorithm
6. **User-Friendly** - Interactive buttons and emojis make data easy to understand

## Technical Notes

### Pattern Matching Order

Handlers are registered in this order to ensure correct routing:
1. `stats:back$` (exact match) - Higher priority
2. `stats:` (prefix match) - Catches `stats:<topic_id>`
3. `topic:` (prefix match) - Separate namespace for quiz topics

### Performance Considerations

- Stats calculations use efficient SQL queries with joins
- Counts and aggregations happen at database level
- No N+1 query problems
- Topic list is filtered to show only topics with progress

### Future Enhancements

Possible improvements discussed with user:
- Daily/weekly streak tracking
- Learning velocity (questions mastered per day)
- Review forecast (questions due tomorrow/this week)
- Achievements/milestones
- Progress comparison over time
- Visual charts (if Telegram supports images)

## Testing

### Manual Testing Steps

1. Start the bot: `python main.py`
2. Type `/stats` in Telegram
3. Verify overall statistics display correctly
4. Tap a topic button
5. Verify detailed topic stats appear
6. Check progress bar renders correctly
7. Tap "Back" button
8. Verify return to main stats menu

### Automated Tests

Run import tests:
```bash
source venv/bin/activate
python3 -c "from src.handlers.callbacks import topic_stats_callback, stats_back_callback; print('✓ Imports successful')"
```

Test repository method:
```bash
source venv/bin/activate
python3 << 'EOF'
from src.database.repository import Repository
import os

db_url = os.getenv('DATABASE_URL', 'sqlite:///learning_bot.db')
repo = Repository(db_url)
stats = repo.get_user_stats(user_id=1, topic_id=None)

assert 'total_questions' in stats
assert 'questions_seen' in stats
assert 'questions_known' in stats
print("✓ All metrics present")
EOF
```

## Troubleshooting

**Issue**: Stats show 0 for all metrics
- **Solution**: User hasn't answered any questions yet. Use `/topics` to start learning.

**Issue**: No topic buttons appear
- **Solution**: User hasn't practiced any topics yet. Start a quiz first.

**Issue**: Callback data error when tapping buttons
- **Solution**: Check handler registration order in `bot.py`. `stats:back` must be registered before `stats:`.

**Issue**: "Known" count seems wrong
- **Solution**: Verify spaced repetition is working. "Known" = `consecutive_correct >= 2`.

## Related Documentation

- [Quiz Behavior](README.md#quiz-behavior) - Explains spaced repetition algorithm
- [Database Schema](src/database/models.py) - UserProgress model fields
- [Commands Menu](COMMANDS_MENU.md) - How to access `/stats` command
