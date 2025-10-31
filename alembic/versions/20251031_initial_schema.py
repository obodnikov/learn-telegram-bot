"""Initial schema.

Revision ID: initial_001
Revises:
Create Date: 2025-10-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the learning bot."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('native_language', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_topics_name'), 'topics', ['name'], unique=False)

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('choice_a', sa.String(length=500), nullable=False),
        sa.Column('choice_b', sa.String(length=500), nullable=False),
        sa.Column('choice_c', sa.String(length=500), nullable=False),
        sa.Column('choice_d', sa.String(length=500), nullable=False),
        sa.Column('correct_answer', sa.String(length=1), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_topic_difficulty', 'questions', ['topic_id', 'difficulty'], unique=False)
    op.create_index('idx_quality_score', 'questions', ['quality_score'], unique=False)
    op.create_index(op.f('ix_questions_difficulty'), 'questions', ['difficulty'], unique=False)
    op.create_index(op.f('ix_questions_topic_id'), 'questions', ['topic_id'], unique=False)

    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('times_shown', sa.Integer(), nullable=False),
        sa.Column('times_correct', sa.Integer(), nullable=False),
        sa.Column('times_incorrect', sa.Integer(), nullable=False),
        sa.Column('consecutive_correct', sa.Integer(), nullable=False),
        sa.Column('last_shown_at', sa.DateTime(), nullable=True),
        sa.Column('next_review_at', sa.DateTime(), nullable=True),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('confidence_rating', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_next_review', 'user_progress', ['user_id', 'next_review_at'], unique=False)
    op.create_index('idx_user_question', 'user_progress', ['user_id', 'question_id'], unique=True)
    op.create_index(op.f('ix_user_progress_question_id'), 'user_progress', ['question_id'], unique=False)
    op.create_index(op.f('ix_user_progress_user_id'), 'user_progress', ['user_id'], unique=False)

    # Create question_analytics table
    op.create_table(
        'question_analytics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('total_times_shown', sa.Integer(), nullable=False),
        sa.Column('total_correct', sa.Integer(), nullable=False),
        sa.Column('total_incorrect', sa.Integer(), nullable=False),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False),
        sa.Column('needs_review', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    op.create_index(op.f('ix_question_analytics_question_id'), 'question_analytics', ['question_id'], unique=False)

    # Create example_file_validations table
    op.create_table(
        'example_file_validations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('validation_status', sa.String(length=20), nullable=False),
        sa.Column('validation_errors', sa.JSON(), nullable=False),
        sa.Column('last_validated_at', sa.DateTime(), nullable=False),
        sa.Column('question_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path')
    )
    op.create_index(op.f('ix_example_file_validations_file_path'), 'example_file_validations', ['file_path'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('example_file_validations')
    op.drop_table('question_analytics')
    op.drop_table('user_progress')
    op.drop_table('questions')
    op.drop_table('topics')
    op.drop_table('users')
