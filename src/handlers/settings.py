"""Settings handlers for user preferences management."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.logger import get_logger
from src.bot import get_bot_instance

logger = get_logger(__name__)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /settings command - Show user settings menu.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"Settings command received from user {user.id}")

    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Get user from database
    db_user = repository.get_user_by_telegram_id(user.id)
    if not db_user:
        await update.message.reply_text(
            "You haven't started any quizzes yet. Use /topics to begin!"
        )
        return

    # Get or create user settings
    user_settings = repository.get_or_create_user_settings(db_user.id)

    # Format current settings
    if user_settings.questions_per_batch:
        current_setting = f"{user_settings.questions_per_batch} questions"
    else:
        current_setting = "Topic default"

    settings_text = (
        f"⚙️ *Your Settings*\n\n"
        f"🔢 *Questions Per Quiz:* {current_setting}\n\n"
        f"_Choose a new value or keep topic defaults:_"
    )

    # Create inline keyboard with batch size options
    keyboard = [
        [
            InlineKeyboardButton("5", callback_data="settings:batch:5"),
            InlineKeyboardButton("10", callback_data="settings:batch:10"),
            InlineKeyboardButton("15", callback_data="settings:batch:15")
        ],
        [
            InlineKeyboardButton("20", callback_data="settings:batch:20"),
            InlineKeyboardButton("25", callback_data="settings:batch:25"),
            InlineKeyboardButton("30", callback_data="settings:batch:30")
        ],
        [
            InlineKeyboardButton("🔄 Use Topic Default", callback_data="settings:batch:default")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        settings_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def settings_batch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle batch size selection callback.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    batch_value = query.data.split(":")[2]

    bot_instance = get_bot_instance()
    repository = bot_instance.repository

    # Get user from database
    db_user = repository.get_user_by_telegram_id(user_id)
    if not db_user:
        await query.edit_message_text("User not found. Please use /start first.")
        return

    # Update settings
    if batch_value == "default":
        # Set to None to use topic defaults
        repository.update_user_settings(db_user.id, questions_per_batch=None)
        setting_display = "Topic default"
        logger.info(f"User {user_id} set questions_per_batch to topic default")
    else:
        # Set to specific value
        batch_size = int(batch_value)
        repository.update_user_settings(db_user.id, questions_per_batch=batch_size)
        setting_display = f"{batch_size} questions"
        logger.info(f"User {user_id} set questions_per_batch to {batch_size}")

    # Confirm the change
    confirmation_text = (
        f"✅ *Settings Updated!*\n\n"
        f"🔢 Questions per quiz: {setting_display}\n\n"
        f"Your next quiz will use this setting.\n"
        f"Use /settings to change it again."
    )

    await query.edit_message_text(
        confirmation_text,
        parse_mode="Markdown"
    )
