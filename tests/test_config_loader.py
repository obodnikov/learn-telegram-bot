"""Tests for config loader."""

import pytest
from pathlib import Path
from src.utils.config_loader import ConfigLoader, TopicConfig
from src.utils.exceptions import ConfigurationError


def test_config_loader_initialization():
    """Test ConfigLoader initialization."""
    # This will fail if config directory doesn't exist
    loader = ConfigLoader("config")
    assert loader.config_dir.exists()


def test_load_topics():
    """Test loading topics configuration."""
    loader = ConfigLoader("config")
    topics = loader.load_topics()
    
    assert len(topics) > 0
    assert "hungarian_vocabulary" in topics
    
    hungarian = topics["hungarian_vocabulary"]
    assert isinstance(hungarian, TopicConfig)
    assert hungarian.target_language == "Hungarian"
    assert hungarian.native_language == "Russian"
    assert hungarian.difficulty == "intermediate"


def test_load_prompts():
    """Test loading prompts configuration."""
    loader = ConfigLoader("config")
    prompts = loader.load_prompts()
    
    assert "question_generation" in prompts
    assert "language" in prompts["question_generation"]


def test_load_difficulty_levels():
    """Test loading difficulty levels."""
    loader = ConfigLoader("config")
    levels = loader.load_difficulty_levels()
    
    assert "beginner" in levels
    assert "intermediate" in levels
    assert "advanced" in levels
    assert "expert" in levels


def test_get_topic():
    """Test getting specific topic."""
    loader = ConfigLoader("config")
    loader.load_all()
    
    topic = loader.get_topic("hungarian_vocabulary")
    assert topic.name == "Hungarian Vocabulary - Everyday Life"


def test_get_topic_not_found():
    """Test getting non-existent topic."""
    loader = ConfigLoader("config")
    loader.load_all()
    
    with pytest.raises(ConfigurationError):
        loader.get_topic("nonexistent_topic")


def test_get_prompt():
    """Test getting prompt template."""
    loader = ConfigLoader("config")
    loader.load_all()
    
    prompt = loader.get_prompt("language", "augment")
    assert len(prompt) > 0
    assert "example" in prompt.lower()


# TODO: Add more tests as implementation progresses
