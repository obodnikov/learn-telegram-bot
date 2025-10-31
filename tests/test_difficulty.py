"""Tests for difficulty management."""

import pytest
from src.utils.difficulty import DifficultyLevel, DifficultyManager


def test_valid_difficulty_levels():
    """Test all valid difficulty levels."""
    valid_levels = ["beginner", "intermediate", "advanced", "expert"]
    
    for level in valid_levels:
        assert DifficultyManager.validate_difficulty(level)


def test_invalid_difficulty_level():
    """Test invalid difficulty levels."""
    invalid_levels = ["easy", "hard", "medium", "novice", "master"]
    
    for level in invalid_levels:
        assert not DifficultyManager.validate_difficulty(level)


def test_difficulty_level_enum():
    """Test DifficultyLevel enum."""
    assert DifficultyLevel.BEGINNER.value == "beginner"
    assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
    assert DifficultyLevel.ADVANCED.value == "advanced"
    assert DifficultyLevel.EXPERT.value == "expert"


def test_get_difficulty_description():
    """Test getting difficulty descriptions."""
    desc = DifficultyManager.get_difficulty_description("beginner")
    assert "basic" in desc.lower()
    
    desc = DifficultyManager.get_difficulty_description("expert")
    assert "academic" in desc.lower()


def test_suggest_difficulty():
    """Test difficulty suggestion based on vocabulary size."""
    # Beginner: < 1000 words
    level = DifficultyManager.suggest_difficulty(500, "language")
    assert level == DifficultyLevel.BEGINNER
    
    # Intermediate: 1000-3000 words
    level = DifficultyManager.suggest_difficulty(2000, "language")
    assert level == DifficultyLevel.INTERMEDIATE
    
    # Advanced: 3000-5000 words
    level = DifficultyManager.suggest_difficulty(4000, "language")
    assert level == DifficultyLevel.ADVANCED
    
    # Expert: 5000+ words
    level = DifficultyManager.suggest_difficulty(6000, "language")
    assert level == DifficultyLevel.EXPERT


def test_case_insensitive_validation():
    """Test case-insensitive difficulty validation."""
    assert DifficultyManager.validate_difficulty("BEGINNER")
    assert DifficultyManager.validate_difficulty("Intermediate")
    assert DifficultyManager.validate_difficulty("aDvAnCeD")
