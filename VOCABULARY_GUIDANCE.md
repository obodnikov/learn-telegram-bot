# Vocabulary Guidance System

Complete guide to the intelligent vocabulary guidance system that prevents question repetition and maintains consistent quality across multiple question generations.

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [The Solution: Hybrid Approach](#the-solution-hybrid-approach)
- [How It Works](#how-it-works)
- [Configuration Examples](#configuration-examples)
- [Benefits](#benefits)
- [Implementation Details](#implementation-details)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Vocabulary Guidance System** is a sophisticated approach to guiding LLM question generation without causing repetitive vocabulary usage. It combines semantic categories with quality calibration to teach the LLM what kind of vocabulary to generate, rather than providing a list to copy from.

**Key Principle**: Instead of telling the LLM "use these specific words," we teach it "generate words with these characteristics."

---

## The Problem

### Traditional Approach (Problematic)

When topic configurations include specific vocabulary lists:

```yaml
Vocabulary categories:
- Adjectives: elkötelezett, kifinomult, elfogult, bonyolult
- Nouns: következmények, hangsúly, lényeg
- Verbs: hangsúlyozni, kétségbe vonni, meggyőzni
```

**What happens:**
1. **First generation**: LLM picks from the list → "elkötelezett", "kifinomult" ✓
2. **Second generation**: LLM picks from the same list → "elfogult", "bonyolult" ✓
3. **Third generation**: LLM runs out of words → starts reusing or picks simpler alternatives ✗
4. **Result**: Repetitive questions, difficulty degradation

### Why It Fails

- LLM treats the list as **the complete vocabulary scope**
- Limited word pool causes **inevitable repetition**
- No guidance on **quality level** when list is exhausted
- **Cycles through categories** predictably

---

## The Solution: Hybrid Approach

The hybrid approach combines three elements:

### 1. Semantic Categories (What to generate)

Instead of specific words, provide **topical areas**:

```yaml
Draw from these semantic categories:
- Adjectives: commitment/dedication-related, sophistication/refinement, bias/prejudice
- Nouns: consequences and outcomes, emphasis and importance, essence and core concepts
- Verbs: emphasizing and stressing, questioning and doubting, convincing and persuading
```

**Purpose**: Guides LLM to the right semantic fields without limiting vocabulary

### 2. Quality Calibration (How complex to make it)

Show examples of **right vs wrong** complexity:

```yaml
QUALITY CALIBRATION (do not reuse these specific words):
✓ Good complexity: elkötelezett (committed/dedicated - nuanced, contextual, C1-C2 level)
✓ Good complexity: kifinomult (sophisticated/refined - abstract quality, multiple meanings)
✗ Too simple: asztal (table - concrete object, beginner A1 level)
✗ Too simple: futni (to run - basic verb, A1-A2 level)
```

**Purpose**: Teaches LLM the exact difficulty threshold

### 3. Explicit Instructions (Don't copy)

Clear directive:

```yaml
Generate NEW vocabulary at the "Good complexity" level.
Do not reuse the calibration examples above - create fresh questions with different vocabulary.
```

**Purpose**: Prevents LLM from copying calibration examples

---

## How It Works

### Step-by-Step Process

1. **LLM reads semantic categories** → Understands topical scope (e.g., "commitment-related adjectives")
2. **LLM studies quality calibration** → Learns what C1-C2 vs A1 looks like
3. **LLM generates vocabulary** → Creates new words matching the calibration level
4. **LLM applies to categories** → Draws from semantic fields with proper complexity

### Example Generation Flow

**Topic**: Hungarian Vocabulary - Advanced

**Input to LLM**:
- Semantic category: "commitment/dedication-related adjectives"
- Quality calibration: ✓ elkötelezett (nuanced, C1-C2) / ✗ nagy (simple, A1)
- Instruction: "Generate NEW vocabulary at this level"

**LLM reasoning**:
1. "I need commitment-related adjectives"
2. "They should be C1-C2 level (nuanced, contextual)"
3. "Not beginner words like 'nagy'"
4. "Don't reuse 'elkötelezett'"

**LLM generates**:
- **First run**: "odaadó" (devoted), "hűséges" (loyal), "állhatatos" (steadfast)
- **Second run**: "rendíthetetlen" (unwavering), "eltökélt" (determined)
- **Third run**: "céltudatos" (goal-oriented), "következetes" (consistent)

**Result**: Infinite scalability without repetition ✅

---

## Configuration Examples

### Advanced Level (C1-C2)

```yaml
hungarian_vocabulary_advanced:
  context: |
    Vocabulary level guidance:
      Generate advanced (C1-C2 level) vocabulary with these characteristics:
      - Abstract concepts requiring contextual understanding (not concrete objects)
      - Words with nuanced meanings and subtle distinctions
      - Formal register used in academic, professional, or literary contexts
      - Idiomatic expressions beyond literal translation
      - Complex compound words and derived forms

      Draw from these semantic categories:
      - Adjectives: commitment/dedication-related, sophistication/refinement, bias/prejudice, complexity, controversy
      - Nouns: consequences and outcomes, emphasis and importance, essence and core concepts, abstract ideas
      - Verbs: emphasizing and stressing, questioning and doubting, convincing and persuading
      - Adverbs: manner and degree (essentially, fundamentally, thoroughly)
      - Idiomatic expressions: figurative language about confidence/doubt, non-literal constructions

      QUALITY CALIBRATION (do not reuse these specific words - they are for complexity reference only):
      ✓ Good complexity: elkötelezett (committed/dedicated - nuanced, contextual, C1-C2 level)
      ✓ Good complexity: kifinomult (sophisticated/refined - abstract quality, multiple meanings)
      ✓ Good complexity: kétségbe vonni (to call into question - idiomatic, non-literal)
      ✓ Good complexity: szemrebbenés nélkül (without batting an eye - pure idiom, cultural)
      ✗ Too simple: asztal (table - concrete object, beginner A1 level)
      ✗ Too simple: futni (to run - basic verb, A1-A2 level)
      ✗ Too simple: nagy (big - common adjective, no nuance required)

      Generate NEW vocabulary at the "Good complexity" level, not the "Too simple" level.
      Do not reuse the calibration examples above - create fresh questions with different vocabulary.
```

### Intermediate Level (B1-B2)

```yaml
hungarian_vocabulary_intermediate:
  context: |
    Vocabulary level guidance:
      Generate intermediate (B1-B2 level) vocabulary with these characteristics:
      - Practical everyday words and phrases for real-life situations
      - Common verbs and their typical usage contexts
      - Useful compound words that intermediate learners should know
      - Vocabulary that appears regularly in everyday Hungarian life

      Draw from these semantic categories:
      - Daily activities: meetings and appointments, shopping and errands, moving and organizing
      - Social situations: neighbors and community, complaining and expressing concern, giving advice
      - Practical needs: making appointments, filling out forms, describing availability
      - Work and life: workplace vocabulary, punctuality and time management, daily routines

      QUALITY CALIBRATION (do not reuse these specific words):
      ✓ Good complexity: találkozó (meeting/appointment - practical, B1-B2 level, useful)
      ✓ Good complexity: időpontot kérni (to request an appointment - compound phrase, practical)
      ✓ Good complexity: átszállni (to change/transfer - specific meaning, requires context)
      ✗ Too simple: menni (to go - basic A1 verb, too elementary)
      ✗ Too simple: nagy (big - basic A1 adjective)
      ✗ Too advanced: elkötelezett (committed - too abstract, C1-C2 level)

      Generate NEW vocabulary at the "Good complexity" level (B1-B2), avoiding both too simple (A1-A2) and too advanced (C1-C2).
      Do not reuse the calibration examples above - create fresh questions with different vocabulary.
```

### Beginner Level (A1-A2)

```yaml
hungarian_vocabulary:
  context: |
    Vocabulary level guidance:
      Generate beginner (A1-A2 level) vocabulary with these characteristics:
      - Common everyday words and basic expressions
      - Essential vocabulary for daily survival situations
      - Simple, concrete words (not abstract concepts)
      - High-frequency words that beginners encounter immediately

      Draw from these semantic categories:
      - Food and meals: basic foods, drinks, ordering, cooking basics
      - Transportation: vehicles, travel, directions, getting around
      - Shopping: buying, paying, basic commerce vocabulary
      - Time expressions: days, hours, when/what time, schedules
      - Greetings and politeness: hello, goodbye, please, thank you

      QUALITY CALIBRATION (do not reuse these specific words):
      ✓ Good complexity: étterem (restaurant - common, practical, A2 level)
      ✓ Good complexity: mennyibe kerül (how much does it cost - essential phrase)
      ✓ Good complexity: busszal utazni (to travel by bus - practical, beginner-appropriate)
      ✗ Too advanced: elkötelezett (committed - abstract, C1-C2 level, too difficult)
      ✗ Too advanced: időpontot kérni (request appointment - intermediate B1-B2)

      Generate NEW vocabulary at the "Good complexity" level (A1-A2), avoiding intermediate and advanced terms.
      Do not reuse the calibration examples above - create fresh questions with different vocabulary.
```

---

## Benefits

### ✅ Prevents Vocabulary Repetition

**Before (specific word lists)**:
- Generation 1: "elkötelezett", "kifinomult"
- Generation 2: "elfogult", "bonyolult"
- Generation 3: Starts reusing or degrading ✗

**After (hybrid guidance)**:
- Generation 1: "odaadó", "rendíthetetlen"
- Generation 2: "eltökélt", "céltudatos"
- Generation 3: "következetes", "állhatatos"
- Generation 100: Still fresh, appropriate vocabulary ✓

### ✅ Maintains Consistent Difficulty

The quality calibration acts as an **anchor** that prevents difficulty drift:

- LLM compares each generated word against calibration examples
- Knows exactly what C1-C2 vs A1 looks like
- Self-corrects if generating too simple or too complex words

### ✅ Scalable to Hundreds of Questions

Unlike finite word lists, semantic categories are **infinite**:

- "Commitment-related adjectives" = unlimited vocabulary
- LLM can generate indefinitely without exhaustion
- Quality remains stable across generations

### ✅ LLM Understands "Why"

Teaching principles instead of words means:

- LLM learns what makes vocabulary "advanced"
- Can apply same logic to any semantic category
- Generalizes beyond specific examples

### ✅ Works Across All Generation Modes

Applies equally to:
- Standard generation (no examples)
- Enhanced generation (with duplicate detection)
- All topic types and difficulty levels

---

## Implementation Details

### File Locations

**Topic Configuration**: [config/topics.yaml](config/topics.yaml)
- Contains vocabulary guidance for each topic
- Lines 12-42 (beginner), 92-118 (advanced), 153-183 (intermediate)

**Prompt Templates**: [config/prompts.yaml](config/prompts.yaml)
- LLM prompt templates that receive the vocabulary guidance
- Templates insert `{context}` placeholder containing guidance

**Question Generator**: [src/services/question_generator.py](src/services/question_generator.py)
- `_build_prompt()` method (lines 500-592) constructs final prompt
- Combines topic config context with prompt templates

### How Context is Passed

1. **Topic config** (`topics.yaml`) defines vocabulary guidance in `context:` field
2. **Config loader** loads topic configuration into memory
3. **Question generator** retrieves topic config and extracts `context`
4. **Prompt builder** inserts context into prompt template via `{context}` placeholder
5. **LLM** receives complete prompt with vocabulary guidance
6. **LLM generates** questions following the guidance

### Technical Flow

```
topics.yaml (vocabulary guidance)
    ↓
ConfigLoader.load_all()
    ↓
QuestionGenerator.generate_questions()
    ↓
_build_prompt(topic_config)
    ↓
prompt_template.format(context=topic_config['context'])
    ↓
LLMService.generate_questions(formatted_prompt)
    ↓
Questions with appropriate vocabulary
```

---

## Best Practices

### 1. Choose Appropriate Semantic Categories

**Good** (broad, principle-based):
```yaml
- Adjectives: commitment/dedication-related, sophistication/refinement
```

**Bad** (too specific, still a word list):
```yaml
- Adjectives: words starting with 'e', words about feelings
```

### 2. Pick Representative Calibration Examples

**Good** (shows clear distinction):
```yaml
✓ Good: elkötelezett (C1-C2, nuanced, contextual)
✗ Too simple: nagy (A1, basic adjective)
```

**Bad** (examples are too similar):
```yaml
✓ Good: elkötelezett (C1-C2)
✗ Too simple: odaadó (C1, also advanced)  # Not enough contrast
```

### 3. Include Multiple Calibration Examples

**Minimum**: 2-3 "good" examples, 2-3 "bad" examples per level

**Why**: More examples = better LLM understanding of the threshold

### 4. Use Clear Explicit Instructions

Always include:
```yaml
Generate NEW vocabulary at the "Good complexity" level.
Do not reuse the calibration examples above.
```

### 5. Match Calibration to Difficulty Level

**Advanced (C1-C2)**: Show abstract vs concrete contrast
**Intermediate (B1-B2)**: Show practical vs too-simple/too-advanced contrast
**Beginner (A1-A2)**: Show essential vs too-advanced contrast

---

## Troubleshooting

### Issue: LLM Still Reuses Calibration Examples

**Symptom**: Generated questions use "elkötelezett" even though calibration says not to

**Solutions**:
1. Make instruction more explicit: "NEVER reuse: elkötelezett, kifinomult..."
2. Add more calibration examples (gives LLM more alternatives)
3. Increase `--recent-context` in enhanced mode to show more existing questions

### Issue: Difficulty Level Drifts

**Symptom**: Advanced topic generates intermediate-level vocabulary

**Solutions**:
1. Add more ✗ examples showing what's "too simple"
2. Make calibration characteristics more specific:
   ```yaml
   ✓ Good: Must be C1-C2, abstract, nuanced, formal register
   ```
3. Include CEFR level explicitly in characteristics

### Issue: Too Generic Vocabulary

**Symptom**: Questions are too broad, don't match topic focus

**Solutions**:
1. Make semantic categories more specific to topic:
   ```yaml
   # Too broad:
   - Verbs: action verbs

   # Better:
   - Verbs: legal argumentation (assert, refute, substantiate)
   ```
2. Add topic-specific calibration examples

### Issue: Repetition Across Semantic Categories

**Symptom**: Different categories generate similar words

**Solutions**:
1. Make categories more distinct:
   ```yaml
   # Too similar:
   - Adjectives: commitment-related
   - Adjectives: dedication-related

   # Better:
   - Adjectives: commitment and loyalty
   - Adjectives: sophistication and refinement
   ```
2. Use enhanced mode with duplicate detection

---

## Related Documentation

- [README.md](README.md) - Main project documentation
- [GENERATE_QUESTIONS.md](GENERATE_QUESTIONS.md) - Question generation guide
- [config/topics.yaml](config/topics.yaml) - Topic configuration with vocabulary guidance
- [config/prompts.yaml](config/prompts.yaml) - LLM prompt templates

---

## Summary

The **Vocabulary Guidance System** solves the question repetition problem by:

1. **Teaching principles** instead of providing word lists
2. **Using semantic categories** for infinite vocabulary scope
3. **Quality calibration** to maintain consistent difficulty
4. **Explicit instructions** to prevent copying examples

**Result**: Scalable, high-quality question generation that can produce hundreds of unique questions without repetition or difficulty degradation.

**Implementation**: Simple YAML configuration in [config/topics.yaml](config/topics.yaml), automatically applied to all generation modes.
