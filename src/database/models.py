"""Database models - placeholder for Phase 2."""

from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class QuestionSource(str, Enum):
    """Source of the question."""
    FILE = "file"
    LLM = "llm"
    HYBRID = "hybrid"


class ValidationStatus(str, Enum):
    """Validation status for example files."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class User:
    """User model."""
    id: int
    telegram_id: int
    native_language: str
    created_at: datetime


@dataclass
class Topic:
    """Topic model."""
    id: int
    name: str
    type: str
    config: dict
    is_active: bool


@dataclass
class Question:
    """Question model."""
    id: int
    topic_id: int
    question_text: str
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    correct_answer: str
    explanation: str
    difficulty: str
    tags: List[str]
    source: QuestionSource
    source_file: Optional[str]
    created_at: datetime
    quality_score: float


@dataclass
class UserProgress:
    """User progress model."""
    id: int
    user_id: int
    question_id: int
    times_shown: int
    times_correct: int
    times_incorrect: int
    consecutive_correct: int
    last_shown_at: Optional[datetime]
    next_review_at: Optional[datetime]
    average_response_time: Optional[float]
    confidence_rating: Optional[int]


@dataclass
class QuestionAnalytics:
    """Question analytics model."""
    id: int
    question_id: int
    total_times_shown: int
    total_correct: int
    total_incorrect: int
    average_response_time: Optional[float]
    success_rate: float
    last_updated_at: datetime
    needs_review: bool


@dataclass
class ExampleFileValidation:
    """Example file validation log model."""
    id: int
    file_path: str
    validation_status: ValidationStatus
    validation_errors: List[str]
    last_validated_at: datetime
    question_count: int


# TODO: Phase 2 - Implement SQLAlchemy models
