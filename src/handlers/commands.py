"""Command handlers for Telegram bot commands."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.logger import get_logger
from src.bot import get_bot_instance

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - Welcome new users and register them.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"Start command received from user {user.id}")

    # Get bot instance
    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Register or get user
    db_user = repository.get_user_by_telegram_id(user.id)
    if not db_user:
        # New user - ask for native language or default to English
        db_user = repository.create_user(
            telegram_id=user.id,
            native_language="English"  # Default, can be changed later
        )
        welcome_text = f"Welcome, {user.first_name}! I'm your learning assistant.\n\n"
    else:
        welcome_text = f"Welcome back, {user.first_name}!\n\n"

    welcome_text += (
        "I help you learn languages and other topics through interactive quizzes "
        "with spaced repetition.\n\n"
        "Use /help to see available commands, or /topics to start learning!"
    )

    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /help command - Show available commands.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    logger.info(f"Help command received from user {user_id}")

    help_text = """
*Available Commands:*

/start - Start the bot and register
/help - Show this help message
/topics - View available learning topics
/stats - View your learning statistics
/settings - Configure your preferences
/cancel - Cancel current quiz session

*How to Use:*

1. Use /topics to see available learning topics
2. Select a topic to start learning
3. Answer questions and get immediate feedback
4. Your progress is tracked automatically with spaced repetition
5. Customize quiz length with /settings

*Features:*

- Spaced repetition algorithm
- Detailed bilingual explanations
- Progress tracking and analytics
- Multiple difficulty levels
- Customizable quiz length per user
    """

    await update.message.reply_text(help_text, parse_mode="Markdown")


async def topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /topics command - Show available topics with selection buttons.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    logger.info(f"Topics command received from user {user_id}")

    # Get bot instance
    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Debug logging
    logger.info(f"Repository database URL: {repository.db_url}")

    # Get all active topics from database
    topics = repository.get_all_topics(active_only=True)
    logger.info(f"Topics query returned {len(topics)} topics (active_only=True)")

    if not topics:
        await update.message.reply_text(
            "No topics available yet. Please contact administrator to add topics."
        )
        return

    # Create inline keyboard with topic buttons
    keyboard = []
    for topic in topics:
        button = InlineKeyboardButton(
            text=topic.name,
            callback_data=f"topic:{topic.id}"
        )
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose a topic to start learning:",
        reply_markup=reply_markup
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /stats command - Show interactive user statistics menu.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"Stats command received from user {user.id}")

    # Get bot instance
    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Get user from database
    db_user = repository.get_user_by_telegram_id(user.id)
    if not db_user:
        await update.message.reply_text(
            "You haven't started any quizzes yet. Use /topics to begin!"
        )
        return

    # Get overall stats
    stats = repository.get_user_stats(db_user.id)

    if stats['questions_seen'] == 0:
        await update.message.reply_text(
            "You haven't answered any questions yet. Use /topics to start learning!"
        )
        return

    # Format overall statistics summary
    stats_text = f"📊 *Your Learning Statistics*\n\n"
    stats_text += f"📚 Total Questions: {stats['total_questions']}\n"
    stats_text += f"👁 Questions Seen: {stats['questions_seen']}\n"
    stats_text += f"🆕 Not Yet Seen: {stats['questions_not_seen']}\n\n"

    stats_text += f"✅ Correct: {stats['total_correct']}\n"
    stats_text += f"❌ Incorrect: {stats['total_incorrect']}\n"
    stats_text += f"🎯 Accuracy: {stats['accuracy'] * 100:.1f}%\n\n"

    stats_text += f"⭐ Known: {stats['questions_known']}\n"
    stats_text += f"📖 Learning: {stats['questions_learning']}\n"
    stats_text += f"⏰ Due for Review: {stats['questions_due']}\n"

    if stats['average_response_time']:
        stats_text += f"\n⚡ Avg Response Time: {stats['average_response_time']:.1f}s"

    if stats['last_activity']:
        from datetime import datetime
        last_activity = stats['last_activity']
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        stats_text += f"\n🕐 Last Activity: {last_activity.strftime('%Y-%m-%d %H:%M')}"

    stats_text += "\n\n_Tap a topic below for detailed stats:_"

    # Create inline keyboard with topic buttons
    topics = repository.get_all_topics(active_only=True)
    keyboard = []

    for topic in topics:
        topic_stats = repository.get_user_stats(db_user.id, topic.id)
        if topic_stats['questions_seen'] > 0:
            # Show topic name with quick stats
            button_text = f"📘 {topic.name} ({topic_stats['questions_seen']}/{topic_stats['total_questions']})"
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"stats:{topic.id}"
            )])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        stats_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /cancel command - Cancel current quiz session.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    logger.info(f"Cancel command received from user {user_id}")

    # Get bot instance
    bot_instance = get_bot_instance()

    # End session if exists
    session = bot_instance.end_session(user_id)

    if session:
        await update.message.reply_text(
            f"Quiz session for '{session['topic_name']}' cancelled.\n"
            f"Questions answered: {session['questions_answered']}\n"
            f"Correct: {session['correct_answers']}\n\n"
            "Use /topics to start a new quiz!"
        )
    else:
        await update.message.reply_text(
            "No active quiz session. Use /topics to start one!"
        )
