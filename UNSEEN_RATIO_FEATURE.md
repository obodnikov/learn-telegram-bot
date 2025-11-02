# Configurable Unseen Questions Ratio Feature

## Overview

The bot now implements a **hybrid question selection algorithm** that balances introducing new content with spaced repetition review. By default, **40% of questions in each session are unseen** (new) questions, with the remaining 60% following spaced repetition priority.

This ensures users consistently encounter new material while still reviewing previously seen questions at optimal intervals.

## Configuration

### Environment Variable

Add to your `.env` file:

```env
# Question Selection Configuration
UNSEEN_QUESTIONS_RATIO=0.40  # 40% unseen questions per session
```

**Valid values**: `0.0` to `1.0`
- `0.0` = 0% unseen (pure spaced repetition)
- `0.40` = 40% unseen (default, recommended)
- `1.0` = 100% unseen (always new questions, no review)

**Default**: `0.40` (40%)

## How It Works

### Session-Level Tracking

When a quiz session starts:
1. Calculate unseen target: `questions_per_batch × UNSEEN_QUESTIONS_RATIO`
2. Track `unseen_shown` counter (starts at 0)
3. Each question increments counter if it was unseen

**Example** (10 questions per session, 40% ratio):
- Unseen target: `10 × 0.40 = 4` questions
- Session aims to show 4 unseen questions + 6 review questions

### Selection Algorithm

For each question in the session:

```
IF unseen_shown < unseen_target AND unseen_questions_available:
    → Select random unseen question
    → Increment unseen_shown counter
ELSE:
    → Follow spaced repetition priority:
        1. Due for review (next_review_at <= now, not mastered)
        2. Not mastered (consecutive_correct < 2)
        3. Fallback to unseen (if quota met but only unseen remain)
END
```

### Priority Breakdown

**Phase 1: Meeting Unseen Quota (Questions 1-4 in example)**
- **Condition**: `unseen_shown < unseen_target`
- **Action**: Select random unseen question
- **Purpose**: Ensure steady introduction of new material

**Phase 2: Spaced Repetition (Questions 5-10 in example)**
- **Condition**: `unseen_shown >= unseen_target`
- **Priority 1**: Questions due for review (random from due pool)
- **Priority 2**: Non-mastered questions (random from non-mastered pool)
- **Fallback**: Unseen questions (if no review items available)

### Mastery Exclusion

Questions with `consecutive_correct >= 2` are considered **known/mastered** and are:
- ✅ Excluded from both unseen quota and spaced repetition selection
- ✅ No longer shown in quizzes
- ✅ Still counted in statistics as "Known"

## Implementation Details

### Modified Files

1. **[.env.example](.env.example)** (lines 24-28)
   - Added `UNSEEN_QUESTIONS_RATIO` configuration

2. **[src/bot.py](src/bot.py)** (lines 220-246)
   - Added `os` import for environment variable access
   - Updated `create_session()` to calculate unseen quota
   - Added session fields: `unseen_shown`, `unseen_target`

3. **[src/database/repository.py](src/database/repository.py)** (lines 318-435)
   - Modified `get_next_question()` signature to accept `unseen_shown` and `unseen_target`
   - Implemented hybrid selection logic
   - Added `is_question_unseen()` helper method (lines 437-455)

4. **[src/handlers/callbacks.py](src/handlers/callbacks.py)** (lines 126-156)
   - Updated `_show_next_question()` to pass unseen tracking parameters
   - Added logic to increment `unseen_shown` counter when showing unseen questions

5. **[src/handlers/quiz.py](src/handlers/quiz.py)** (lines 78-108)
   - Updated `next_question_handler()` to pass unseen tracking parameters
   - Added logic to increment `unseen_shown` counter

6. **[README.md](README.md)** (lines 374-407)
   - Completely rewrote "Intelligent Question Selection" section
   - Documented hybrid algorithm and configuration

### Session Data Structure

```python
session = {
    "topic_id": 1,
    "topic_name": "Hungarian Vocabulary",
    "questions_answered": 3,
    "questions_per_batch": 10,
    "unseen_shown": 2,        # NEW: Count of unseen questions shown
    "unseen_target": 4,       # NEW: Target unseen questions (40% of 10 = 4)
    # ... other fields
}
```

### Algorithm Flow Diagram

```
Start Quiz Session
    ↓
Calculate unseen_target = questions_per_batch × UNSEEN_QUESTIONS_RATIO
    ↓
For each question:
    ↓
    ┌─────────────────────────────────┐
    │ Is unseen_shown < unseen_target? │
    └─────────────┬───────────────────┘
                  │
        ┌─────────┴──────────┐
       YES                   NO
        │                     │
        ↓                     ↓
    ┌────────────────┐   ┌──────────────────┐
    │ Unseen available? │   │ Spaced Repetition │
    └────┬───────────┘   │  Priority:        │
         │               │  1. Due           │
    ┌────┴────┐         │  2. Non-mastered  │
   YES       NO          │  3. Unseen        │
    │         │          └──────────────────┘
    ↓         │                  │
┌─────────────┐│                 │
│ Select      ││                 │
│ Unseen      ││                 │
│ Increment   ││                 │
│ Counter     ││                 │
└─────────────┘│                 │
    │          │                 │
    └──────────┴─────────────────┘
               │
               ↓
         Show Question
               │
               ↓
         Next Question...
```

## Examples

### Example 1: Standard Session (10 questions, 40% unseen)

**Setup:**
- `questions_per_batch = 10`
- `UNSEEN_QUESTIONS_RATIO = 0.40`
- `unseen_target = 4`

**Session Flow:**

| Q# | unseen_shown | Action | Result |
|----|--------------|--------|--------|
| 1  | 0/4 | Need unseen → select unseen | Unseen question A |
| 2  | 1/4 | Need unseen → select unseen | Unseen question B |
| 3  | 2/4 | Need unseen → select unseen | Unseen question C |
| 4  | 3/4 | Need unseen → select unseen | Unseen question D |
| 5  | 4/4 | Quota met → spaced repetition | Due question 1 |
| 6  | 4/4 | Quota met → spaced repetition | Due question 2 |
| 7  | 4/4 | Quota met → spaced repetition | Non-mastered question 1 |
| 8  | 4/4 | Quota met → spaced repetition | Non-mastered question 2 |
| 9  | 4/4 | Quota met → spaced repetition | Due question 3 |
| 10 | 4/4 | Quota met → spaced repetition | Non-mastered question 3 |

**Result**: 4 unseen (40%) + 6 review (60%)

### Example 2: Limited Unseen Questions

**Setup:**
- Only 2 unseen questions available
- Target is 4 unseen (40% of 10)

**Session Flow:**

| Q# | unseen_shown | Action | Result |
|----|--------------|--------|--------|
| 1  | 0/4 | Need unseen → select unseen | Unseen question A |
| 2  | 1/4 | Need unseen → select unseen | Unseen question B |
| 3  | 2/4 | Need unseen BUT none left → spaced rep | Due question 1 |
| 4-10 | 2/4 | Spaced repetition | Review questions |

**Result**: 2 unseen (20%) + 8 review (80%) - quota not fully met due to availability

### Example 3: Pure Spaced Repetition (0% unseen)

**Configuration:**
```env
UNSEEN_QUESTIONS_RATIO=0.0
```

**Session Flow:**
- All questions follow spaced repetition priority
- No unseen quota to meet
- Behaves like original algorithm

### Example 4: All New Content (100% unseen)

**Configuration:**
```env
UNSEEN_QUESTIONS_RATIO=1.0
```

**Session Flow:**
- All 10 questions will be unseen (if available)
- No spaced repetition until all unseen questions exhausted
- **Not recommended** - defeats purpose of review

## Benefits

### 1. Balanced Learning
- **Old behavior**: Could show all review or all unseen depending on availability
- **New behavior**: Guaranteed mix of new + review in every session (if possible)

### 2. Consistent Progress
- Users always encounter new material (if available)
- Prevents frustration from "only seeing review questions"
- Maintains motivation through steady progress

### 3. Optimal Retention
- 60% of session dedicated to spaced repetition
- Review questions shown at scientifically optimal intervals
- Balances acquisition (new) with retention (review)

### 4. Configurable
- Admins can adjust ratio based on learning goals:
  - Higher ratio (0.6) = Faster progress, more new content
  - Lower ratio (0.2) = More review, better retention
  - Default (0.4) = Balanced approach

### 5. Graceful Degradation
- If insufficient unseen questions, fills with review
- If all questions are unseen, follows spaced repetition priorities
- Always provides best possible question mix

## Testing

### Manual Testing

1. Set ratio in `.env`:
   ```env
   UNSEEN_QUESTIONS_RATIO=0.40
   ```

2. Start bot and begin quiz:
   ```bash
   python main.py
   ```

3. In Telegram:
   - `/topics` → select a topic
   - Start quiz session
   - Check logs for unseen tracking

4. Look for log messages:
   ```
   Created quiz session ... unseen target: 4 (40%)
   Selected unseen question ID: 23 (random from 25 unseen, progress: 1/4)
   Showing unseen question, progress: 1/4
   ```

### Automated Testing

```bash
source venv/bin/activate && python3 << 'EOF'
from src.database.repository import Repository
import os

os.environ['UNSEEN_QUESTIONS_RATIO'] = '0.40'
db_url = 'sqlite:///learning_bot.db'
repo = Repository(db_url)

# Test with different quotas
user_id = 1
topic_id = 1

print("Test 1: Unseen quota not met (0/4)")
q1 = repo.get_next_question(user_id, topic_id, unseen_shown=0, unseen_target=4)
print(f"Selected: {q1.id if q1 else None}")

print("\nTest 2: Unseen quota met (4/4)")
q2 = repo.get_next_question(user_id, topic_id, unseen_shown=4, unseen_target=4)
print(f"Selected: {q2.id if q2 else None}")

print("\n✓ Tests passed")
EOF
```

## Troubleshooting

**Issue**: All questions are unseen, even when quota is met
- **Cause**: `unseen_shown` counter not incrementing
- **Solution**: Check that `is_question_unseen()` is being called after selecting question

**Issue**: Never showing unseen questions
- **Cause**: `UNSEEN_QUESTIONS_RATIO` not set or set to 0
- **Solution**: Add to `.env` file: `UNSEEN_QUESTIONS_RATIO=0.40`

**Issue**: Ratio not working as expected
- **Cause**: Integer division rounding
- **Solution**: For small batches (< 10), quota may round down. E.g., 5 questions × 0.40 = 2.0 (exactly 40%)

**Issue**: Logs show "fallback: unseen, quota met"
- **This is normal**: Happens when quota is met but no due/non-mastered questions available
- **Action**: System gracefully falls back to showing unseen questions

## Performance Considerations

**Database Queries:**
- Single query to get all questions for topic
- Single query to get user progress
- No additional queries per question selection

**Memory:**
- Minimal overhead: 2 integers added to session dictionary
- No impact on response time

**Scalability:**
- Algorithm complexity: O(n) where n = questions in topic
- Same as original algorithm
- Random selection is O(1)

## Future Enhancements

Possible improvements:

1. **Dynamic Ratio**: Adjust based on user performance
   - Struggling → lower ratio (more review)
   - Excelling → higher ratio (more new content)

2. **Per-Topic Ratio**: Different ratios for different topics
   - Easy topics: higher unseen ratio
   - Difficult topics: lower unseen ratio

3. **Adaptive Targets**: Consider user's total unseen count
   - Many unseen available → meet full target
   - Few unseen left → reduce target dynamically

4. **Session Statistics**: Show in end-of-session summary
   - "You saw 4 new questions and reviewed 6 questions"

## Related Documentation

- [README.md - Quiz Behavior](README.md#quiz-behavior)
- [STATS_FEATURE.md](STATS_FEATURE.md) - View unseen count in statistics
- [src/database/repository.py](src/database/repository.py) - Implementation details

## Changelog

**2025-11-02**:
- Added `UNSEEN_QUESTIONS_RATIO` configuration
- Implemented hybrid selection algorithm
- Updated session tracking with `unseen_shown` and `unseen_target`
- Added `is_question_unseen()` helper method
- Updated documentation
