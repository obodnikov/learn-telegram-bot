"""Quiz interaction handlers for managing quiz sessions."""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def start_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /quiz command - Show topic selection or continue existing session.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    logger.info(f"Quiz command received from user {user_id}")

    bot_instance = context.bot_data.get("bot_instance")
    if not bot_instance:
        await update.message.reply_text("Bot not properly initialized.")
        return

    # Check for existing session
    session = bot_instance.get_session(user_id)
    if session:
        await update.message.reply_text(
            f"You already have an active quiz for '{session['topic_name']}'.\n"
            "Use /cancel to end it first, or continue answering questions."
        )
        return

    # Show topics
    await update.message.reply_text(
        "Use /topics to select a topic for your quiz session!"
    )


async def next_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show next question in quiz session.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    bot_instance = context.bot_data.get("bot_instance")

    if not bot_instance:
        await query.edit_message_text("Bot not properly initialized.")
        return

    session = bot_instance.get_session(user_id)
    if not session:
        await query.edit_message_text(
            "No active quiz session. Use /topics to start one!"
        )
        return

    # Get next question using spaced repetition
    repository = bot_instance.repository
    db_user = repository.get_user_by_telegram_id(user_id)

    question = repository.get_next_question(db_user.id, session['topic_id'])

    if not question:
        await query.edit_message_text(
            f"No more questions available for '{session['topic_name']}'.\n\n"
            f"Session complete!\n"
            f"Questions answered: {session['questions_answered']}\n"
            f"Correct: {session['correct_answers']}\n"
            f"Accuracy: {session['correct_answers']/session['questions_answered']*100 if session['questions_answered'] > 0 else 0:.1f}%"
        )
        bot_instance.end_session(user_id)
        return

    # Store current question and start time
    session['current_question'] = question
    session['start_time'] = datetime.utcnow()

    # Create answer buttons
    keyboard = [
        [InlineKeyboardButton("A", callback_data=f"answer:A")],
        [InlineKeyboardButton("B", callback_data=f"answer:B")],
        [InlineKeyboardButton("C", callback_data=f"answer:C")],
        [InlineKeyboardButton("D", callback_data=f"answer:D")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Format question text
    question_text = f"*Question:*\n{question.question_text}\n\n"
    question_text += f"A: {question.choice_a}\n"
    question_text += f"B: {question.choice_b}\n"
    question_text += f"C: {question.choice_c}\n"
    question_text += f"D: {question.choice_d}\n"

    await query.edit_message_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
