"""Quiz interaction handlers - placeholder for Phase 3."""

from telegram import Update
from telegram.ext import ContextTypes
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start a quiz session.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    # TODO: Phase 3 - Implement quiz session
    logger.info(f"Quiz started for user {update.effective_user.id}")
    pass


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user's answer to a question.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    # TODO: Phase 3 - Process answer and update progress
    logger.info(f"Answer received from user {update.effective_user.id}")
    pass


async def show_explanation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show explanation for the current question.
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    # TODO: Phase 3 - Display explanation
    logger.info(f"Explanation requested by user {update.effective_user.id}")
    pass
