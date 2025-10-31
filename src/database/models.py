"""Database models for SQLAlchemy."""

from __future__ import annotations
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, JSON, Text,
    ForeignKey, create_engine, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


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


class User(Base):
    """User model for storing Telegram user information."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    native_language: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    progress: Mapped[list["UserProgress"]] = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"


class Topic(Base):
    """Topic model for learning topics."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, name={self.name}, type={self.type})>"


class Question(Base):
    """Question model for quiz questions."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    choice_a: Mapped[str] = mapped_column(String(500), nullable=False)
    choice_b: Mapped[str] = mapped_column(String(500), nullable=False)
    choice_c: Mapped[str] = mapped_column(String(500), nullable=False)
    choice_d: Mapped[str] = mapped_column(String(500), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="questions")
    progress: Mapped[list["UserProgress"]] = relationship("UserProgress", back_populates="question", cascade="all, delete-orphan")
    analytics: Mapped[Optional["QuestionAnalytics"]] = relationship("QuestionAnalytics", back_populates="question", uselist=False, cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_topic_difficulty', 'topic_id', 'difficulty'),
        Index('idx_quality_score', 'quality_score'),
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, topic_id={self.topic_id}, difficulty={self.difficulty})>"


class UserProgress(Base):
    """User progress model for tracking performance on questions."""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    times_shown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_incorrect: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consecutive_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_shown_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    average_response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress")
    question: Mapped["Question"] = relationship("Question", back_populates="progress")

    # Indexes for spaced repetition queries
    __table_args__ = (
        Index('idx_user_next_review', 'user_id', 'next_review_at'),
        Index('idx_user_question', 'user_id', 'question_id', unique=True),
    )

    def __repr__(self) -> str:
        return f"<UserProgress(user_id={self.user_id}, question_id={self.question_id}, consecutive_correct={self.consecutive_correct})>"


class QuestionAnalytics(Base):
    """Question analytics model for tracking question performance."""

    __tablename__ = "question_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), unique=True, nullable=False, index=True)
    total_times_shown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_incorrect: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="analytics")

    def __repr__(self) -> str:
        return f"<QuestionAnalytics(question_id={self.question_id}, success_rate={self.success_rate:.2f})>"


class ExampleFileValidation(Base):
    """Example file validation log model."""

    __tablename__ = "example_file_validations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    validation_status: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_errors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    last_validated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<ExampleFileValidation(file_path={self.file_path}, status={self.validation_status})>"
