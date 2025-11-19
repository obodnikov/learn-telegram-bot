"""add_topic_history_table

Revision ID: c9de22860740
Revises: df5ca33e4879
Create Date: 2025-11-19 09:08:32.174578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9de22860740'
down_revision: Union[str, None] = 'df5ca33e4879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create topic_history table for tracking completed topic attempts."""
    op.create_table(
        'topic_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('completion_date', sa.DateTime(), nullable=False),
        sa.Column('questions_total', sa.Integer(), nullable=False),
        sa.Column('questions_correct', sa.Integer(), nullable=False),
        sa.Column('questions_incorrect', sa.Integer(), nullable=False),
        sa.Column('accuracy_percentage', sa.Float(), nullable=False),
        sa.Column('questions_known', sa.Integer(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_topic_history', 'topic_history', ['user_id', 'topic_id'], unique=False)
    op.create_index(op.f('ix_topic_history_topic_id'), 'topic_history', ['topic_id'], unique=False)
    op.create_index(op.f('ix_topic_history_user_id'), 'topic_history', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop topic_history table."""
    op.drop_index(op.f('ix_topic_history_user_id'), table_name='topic_history')
    op.drop_index(op.f('ix_topic_history_topic_id'), table_name='topic_history')
    op.drop_index('idx_user_topic_history', table_name='topic_history')
    op.drop_table('topic_history')
