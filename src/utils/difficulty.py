"""Difficulty level management and validation."""
from enum import Enum
from typing import List
from dataclasses import dataclass


class DifficultyLevel(str, Enum):
    """Available difficulty levels for questions."""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class DifficultyCriteria:
    """Criteria for a difficulty level."""
    
    description: str
    language_criteria: List[str]
    history_criteria: List[str]
    distractor_complexity: str
    explanation_depth: str


class DifficultyManager:
    """Manage difficulty levels and validation."""
    
    VALID_LEVELS = [level.value for level in DifficultyLevel]
    
    @staticmethod
    def validate_difficulty(difficulty: str) -> bool:
        """
        Check if difficulty level is valid.
        
        Args:
            difficulty: Difficulty string to validate
            
        Returns:
            True if valid, False otherwise
        """
        return difficulty.lower() in DifficultyManager.VALID_LEVELS
    
    @staticmethod
    def get_difficulty_description(difficulty: str) -> str:
        """
        Get human-readable description of difficulty level.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Description string
        """
        descriptions = {
            "beginner": "Basic concepts and common vocabulary",
            "intermediate": "Moderate complexity with cultural context",
            "advanced": "Complex structures and specialized knowledge",
            "expert": "Academic level with professional terminology"
        }
        return descriptions.get(difficulty.lower(), "Unknown difficulty")
    
    @staticmethod
    def suggest_difficulty(
        vocabulary_size: int, 
        topic_type: str
    ) -> DifficultyLevel:
        """
        Suggest appropriate difficulty based on metrics.
        
        Args:
            vocabulary_size: Number of words/concepts
            topic_type: Type of topic (language, history, etc.)
            
        Returns:
            Suggested difficulty level
        """
        if vocabulary_size < 1000:
            return DifficultyLevel.BEGINNER
        elif vocabulary_size < 3000:
            return DifficultyLevel.INTERMEDIATE
        elif vocabulary_size < 5000:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT
