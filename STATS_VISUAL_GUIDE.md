# Interactive Statistics - Visual Guide

## User Journey

### Step 1: Type `/stats`

User types the `/stats` command in Telegram.

### Step 2: Overall Statistics Screen

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

Tap a topic below for detailed stats:

┌────────────────────────────────────┐
│ 📘 Hungarian Vocabulary - Beginner │
│            (6/15)                  │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ 📘 Hungarian Vocabulary - Advanced │
│            (6/15)                  │
└────────────────────────────────────┘
```

**What this shows:**
- **Total Questions (30)**: All questions across all topics in the database
- **Questions Seen (12)**: User has encountered 12 different questions
- **Not Yet Seen (18)**: 18 questions the user hasn't seen yet
- **Correct/Incorrect**: Answer history
- **Accuracy (75%)**: Success rate
- **Known (4)**: Questions mastered (2+ consecutive correct answers)
- **Learning (8)**: Questions seen but not yet mastered
- **Due for Review (3)**: Questions that need practice now (spaced repetition)
- **Topic Buttons**: Shows "seen/total" for each topic

### Step 3: User Taps a Topic Button

User taps on "📘 Hungarian Vocabulary - Beginner (6/15)"

### Step 4: Detailed Topic Statistics

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

┌────────────────────────────────────┐
│      « Back to All Stats           │
└────────────────────────────────────┘
```

**What this shows:**
- All the same metrics, but filtered to just this one topic
- **Progress Bar**: Visual representation of mastery (2 known / 15 total = 13.3%)
- **Mastery Level**: Percentage of questions in this topic that are "known"
- **Back Button**: Returns to the overall statistics screen

### Step 5: User Taps "Back" Button

Returns to the overall statistics screen (Step 2).

## Metrics Explanation

### Questions Status

```
┌─────────────── Total Questions (30) ──────────────┐
│                                                    │
│  ┌──── Seen (12) ────┐                           │
│  │                    │                           │
│  │ ┌─ Known (4) ─┐   │                           │
│  │ │              │   │                           │
│  │ └──────────────┘   │      Not Yet Seen (18)   │
│  │                    │                           │
│  │ Learning (8)       │                           │
│  │                    │                           │
│  └────────────────────┘                           │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Breakdown:**
- **Total Questions**: All questions in database for this topic/all topics
- **Questions Seen**: Questions user has encountered at least once
- **Not Yet Seen**: `Total - Seen` (questions never shown to user)
- **Known**: Questions with 2+ consecutive correct answers (mastered, excluded from future quizzes)
- **Learning**: `Seen - Known` (questions user is still practicing)

### Review Status

```
┌──── Questions Learning (8) ────┐
│                                 │
│  Due for Review (3)            │
│  (need practice NOW)           │
│                                 │
│  Not Due Yet (5)               │
│  (will be reviewed later)      │
│                                 │
└─────────────────────────────────┘
```

**Due for Review:**
- Questions where `next_review_at <= now`
- Only counts "Learning" questions (not "Known")
- These are the questions the spaced repetition algorithm wants you to practice right now

### Performance Metrics

```
Total Attempts = Correct + Incorrect
Accuracy = Correct / Total Attempts × 100%

Example:
15 Correct + 5 Incorrect = 20 Total Attempts
Accuracy = 15 / 20 × 100% = 75.0%
```

### Progress Bar

```
Mastery Level = Known / Total Questions × 100%

Example:
2 Known / 15 Total = 13.3%

Visual:
0%    10%   20%   30%   40%   50%   60%   70%   80%   90%  100%
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
████░░░░░░ 13%

10 blocks total:
- Filled (█): 1 block (13% ≈ 1.3 blocks, rounded down to 1)
- Empty (░): 9 blocks
```

## Emoji Legend

| Emoji | Meaning |
|-------|---------|
| 📊 | Statistics |
| 📚 | Total/Library |
| 👁 | Seen/Viewed |
| 🆕 | New/Not Yet Seen |
| ✅ | Correct |
| ❌ | Incorrect |
| 🎯 | Accuracy/Target |
| ⭐ | Known/Mastered |
| 📖 | Learning |
| ⏰ | Due for Review |
| ⚡ | Speed/Fast |
| 🕐 | Time/Clock |
| 📈 | Progress/Growth |
| 📘 | Topic/Book |

## Color Coding (if Telegram supports it)

While the current implementation uses emojis, Telegram's markdown doesn't support colors. However, the emojis provide visual distinction:

- 📚📘 Blue book emojis for questions/topics
- ✅ Green checkmark for correct/success
- ❌ Red X for incorrect/errors
- ⭐ Gold star for mastery
- ⏰ Clock for urgency (due items)

## Navigation Pattern

```
/stats Command
     ↓
┌─────────────────────┐
│  Overall Stats      │ ← Main hub
│  [Topic Buttons]    │
└─────────────────────┘
     ↓ (tap topic)
┌─────────────────────┐
│  Topic Details      │
│  [Back Button]      │
└─────────────────────┘
     ↓ (tap back)
┌─────────────────────┐
│  Overall Stats      │ ← Returns to main hub
│  [Topic Buttons]    │
└─────────────────────┘
```

## Real-World Example

### Scenario: Learning Hungarian

**User Progress:**
- Beginner topic: Started, 6 questions seen out of 15
- Advanced topic: Started, 6 questions seen out of 15
- Total across both topics: 12 seen out of 30

**Overall Screen Shows:**
```
📊 Your Learning Statistics

📚 Total Questions: 30          ← Both topics combined
👁 Questions Seen: 12            ← 6 + 6 from both topics
🆕 Not Yet Seen: 18              ← 30 - 12 = 18 remaining

✅ Correct: 15                   ← All correct answers
❌ Incorrect: 5                  ← All incorrect answers
🎯 Accuracy: 75.0%               ← 15/(15+5) = 75%

⭐ Known: 4                      ← 2 from beginner + 2 from advanced
📖 Learning: 8                   ← 12 seen - 4 known = 8
⏰ Due for Review: 3             ← Needs practice now

⚡ Avg Response Time: 8.5s       ← Average across all answers
🕐 Last Activity: 2025-11-02     ← Most recent practice

Tap a topic below for detailed stats:

[📘 Hungarian Vocabulary - Beginner (6/15)]  ← 6 seen, 15 total
[📘 Hungarian Vocabulary - Advanced (6/15)]  ← 6 seen, 15 total
```

**User taps "Beginner" button:**
```
📊 Hungarian Vocabulary - Beginner
========================================

Question Progress:
📚 Total Questions: 15           ← This topic only
👁 Questions Seen: 6             ← This topic only
🆕 Not Yet Seen: 9               ← 15 - 6 = 9

Performance:
✅ Correct: 8                    ← This topic only
❌ Incorrect: 2                  ← This topic only
🎯 Accuracy: 80.0%               ← 8/(8+2) = 80%

Learning Status:
⭐ Known: 2                      ← Mastered from this topic
📖 Learning: 4                   ← 6 seen - 2 known = 4
⏰ Due for Review: 1             ← From this topic

Speed:
⚡ Avg Response Time: 7.2s       ← This topic's average

Activity:
🕐 Last Practiced: 2025-11-02 10:15  ← Last time practiced THIS topic

Overall Progress:
📈 Mastery Level: 13.3%          ← 2 known / 15 total = 13.3%
████░░░░░░ 13%                   ← Visual progress bar

[« Back to All Stats]
```

## Benefits for Users

1. **Motivation**: See progress bars fill up as you learn
2. **Focus**: "Due for Review" tells you exactly what to practice
3. **Insight**: Accuracy shows which topics need more work
4. **Organization**: Manage multiple topics separately
5. **Gamification**: Watch "Known" count increase
6. **Efficiency**: Visual indicators make stats easy to scan
7. **Flexibility**: Drill down into topics you care about
