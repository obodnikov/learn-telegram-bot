# Question Refinement Guide

## Overview

This guide explains how to improve question quality over time using the bot's analytics and tracking features.

## Quality Metrics

The bot tracks several metrics for each question:

### Success Rate
- **Formula**: `correct_answers / total_attempts`
- **Target**: 40-70% for good questions
- **Too Low (<40%)**: Question may be unclear or too difficult
- **Too High (>80%)**: Question may be too easy

### Response Time
- **Metric**: Average time to answer (seconds)
- **Analysis**: 
  - Very fast (<5s): May be too obvious
  - Very slow (>60s): May be confusing or require too much thinking

### Consecutive Correct Answers
- **Metric**: How many times users get it right in a row
- **Target**: Users should need 2-3 attempts to master
- **Too Easy**: Correct on first try consistently

## Identifying Problems

### Low-Quality Questions (Quality Score < 0.4)

Common issues:
1. **Ambiguous wording**: Multiple interpretations possible
2. **Trick questions**: Deliberately misleading
3. **Too specific**: Requires memorization rather than understanding
4. **Cultural bias**: Assumes knowledge outside the topic
5. **Poor distractors**: All wrong answers obviously wrong

### High-Quality Questions (Quality Score > 0.8)

Characteristics:
- Clear, unambiguous question
- One correct answer, three plausible distractors
- Tests understanding, not just memory
- Appropriate difficulty for level
- Rich, educational explanation

## Refinement Process

### 1. Review Analytics

Check question performance:
```bash
# View questions needing review
python scripts/review_questions.py --min-attempts 10 --max-quality 0.4

# Export stats
python scripts/export_stats.py --topic hungarian_vocabulary
```

### 2. Analyze Patterns

Look for:
- Questions with <40% success rate
- Questions answered too quickly (<5s average)
- Questions where users plateau (stop improving)

### 3. Improve Questions

#### Fix Ambiguous Questions
❌ **Before**: "What does 'run' mean?"
✅ **After**: "In the sentence 'I run every morning', what does 'run' mean?"

#### Improve Distractors
❌ **Before**: 
```
Q: When did WWII start?
A: 1939
B: 1776
C: 2020
D: 500 BC
```

✅ **After**:
```
Q: When did WWII start?
A: 1939
B: 1914  (WWI start)
C: 1941  (Pearl Harbor)
D: 1945  (WWII end)
```

#### Enhance Explanations
❌ **Before**: "'Hola' means 'hello' in Spanish."

✅ **After**: 
```
Spanish: 'Hola' is the most common greeting in Spanish, used throughout 
the day in both formal and informal contexts. It's equivalent to 'hello' 
or 'hi' in English.

Russian: 'Hola' - самое распространенное приветствие на испанском языке, 
используется в течение всего дня как в формальных, так и в неформальных 
ситуациях. Эквивалент английского 'hello' или 'hi'.
```

### 4. Update Example Files

Add improved questions to example files:

```json
{
  "meta": {
    "topic": "hungarian_vocabulary",
    "version": "2.0",
    "last_updated": "2025-10-30",
    "changes": "Improved distractors based on analytics"
  },
  "questions": [
    // Updated questions here
  ]
}
```

### 5. Regenerate Questions

The bot will use updated examples for future question generation.

## Best Practices

### Question Writing

1. **One Concept Per Question**: Don't test multiple things
2. **Clear Language**: Avoid complex sentence structures
3. **No Tricks**: Test understanding, not reading comprehension
4. **Progressive Difficulty**: Start easy, build up
5. **Real-World Context**: Use practical examples

### Explanation Writing

1. **Bilingual for Languages**: Always provide both languages
2. **Why, Not Just What**: Explain reasoning
3. **Cultural Context**: Add relevant background
4. **Examples**: Show usage in context
5. **Mnemonics**: Provide memory aids when helpful

### Distractor Creation

1. **Plausible**: Should be believable to someone unsure
2. **Common Mistakes**: Use typical learner errors
3. **Similar Options**: Close to correct answer
4. **No Patterns**: Avoid always making 'B' correct
5. **Different Types**: Mix close matches with opposites

## Automated Improvement

The bot can help identify improvements:

### Flag Questions for Review
```python
# Questions are automatically flagged when:
- Success rate < 40% after 20+ attempts
- Average response time > 60 seconds
- Quality score < 0.4
```

### Export Top Questions
```bash
# Get best questions for a topic
python scripts/export_best_questions.py \
  --topic hungarian_vocabulary \
  --min-quality 0.8 \
  --output config/examples/hungarian_vocabulary_v2.json
```

### Compare Versions
Track improvements over time:
```bash
python scripts/compare_versions.py \
  --old hungarian_vocabulary_v1.json \
  --new hungarian_vocabulary_v2.json
```

## Quality Checklist

Before adding a question to examples:

- [ ] Question is clear and unambiguous
- [ ] Has exactly one correct answer
- [ ] Three plausible distractors
- [ ] Explanation is detailed and educational
- [ ] Appropriate difficulty level
- [ ] Proper tags applied
- [ ] Tested with sample users
- [ ] Bilingual explanation (for language topics)

## Monitoring

### Weekly Review
1. Check analytics dashboard
2. Review flagged questions
3. Update 1-2 example files
4. Regenerate questions

### Monthly Analysis
1. Compare topic performance
2. Identify patterns
3. Update difficulty levels if needed
4. Refresh old questions

### Quarterly Refresh
1. Major example file updates
2. Add new question types
3. Remove outdated content
4. Adjust generation parameters

## Getting User Feedback

### In-Bot Feedback
- Add confidence rating after each answer
- Track questions users skip
- Monitor completion rates

### Manual Review
- Ask users for problem questions
- Test with focus groups
- Iterate based on feedback

## Conclusion

Quality questions are built through iteration. Use analytics to guide improvements, 
test changes, and continuously refine your question bank. The goal is questions that 
challenge learners appropriately while teaching effectively.
