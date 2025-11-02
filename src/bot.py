"""Main bot module for Telegram bot initialization and management."""

from typing import Optional, Dict, Any
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from src.utils.logger import get_logger
from src.database.repository import Repository
from src.services.llm_service import LLMService
from src.services.question_generator import QuestionGenerator
from src.services.example_parser import ExampleParser
from src.services.scheduler import QuestionScheduler
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)

# Global bot instance (set during initialization)
_bot_instance: Optional['LearningBot'] = None


def get_bot_instance() -> 'LearningBot':
    """Get the global bot instance."""
    if _bot_instance is None:
        raise RuntimeError("Bot instance not initialized")
    return _bot_instance


class LearningBot:
    """Telegram learning bot main class."""

    def __init__(
        self,
        token: str,
        repository: Repository,
        config_loader: ConfigLoader,
        llm_service: Optional[LLMService] = None,
        enable_scheduler: bool = False
    ):
        """
        Initialize the learning bot.

        Args:
            token: Telegram bot token
            repository: Database repository instance
            config_loader: Configuration loader instance
            llm_service: Optional LLM service for question generation
            enable_scheduler: Whether to enable automatic question generation scheduler
        """
        self.token = token
        self.repository = repository
        self.config_loader = config_loader
        self.llm_service = llm_service

        # Initialize services
        self.example_parser = ExampleParser()
        if llm_service:
            self.question_generator = QuestionGenerator(
                llm_service, config_loader, self.example_parser, repository
            )

            # Initialize scheduler if enabled
            if enable_scheduler:
                self.scheduler = QuestionScheduler(
                    repository, self.question_generator, config_loader
                )
                logger.info("Scheduler initialized")
            else:
                self.scheduler = None
        else:
            self.question_generator = None
            self.scheduler = None

        # Session management - stores active quiz sessions
        self.active_sessions: Dict[int, Dict[str, Any]] = {}

        # Create application
        self.application = Application.builder().token(token).build()

        # Set global bot instance
        global _bot_instance
        _bot_instance = self

        # Register handlers
        self._register_handlers()

        logger.info("LearningBot initialized successfully")

    def _register_handlers(self) -> None:
        """Register all command and callback handlers."""
        from src.handlers.commands import (
            start_command, help_command, topics_command,
            stats_command, cancel_command
        )
        from src.handlers.quiz import start_quiz_handler, next_question_handler
        from src.handlers.callbacks import (
            topic_selection_callback, answer_callback,
            show_explanation_callback, topic_stats_callback,
            stats_back_callback
        )

        # Command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("topics", topics_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("quiz", start_quiz_handler))
        self.application.add_handler(CommandHandler("cancel", cancel_command))

        # Callback query handlers (for inline buttons)
        self.application.add_handler(CallbackQueryHandler(
            topic_selection_callback, pattern="^topic:"
        ))
        self.application.add_handler(CallbackQueryHandler(
            answer_callback, pattern="^answer:"
        ))
        self.application.add_handler(CallbackQueryHandler(
            show_explanation_callback, pattern="^explain:"
        ))
        self.application.add_handler(CallbackQueryHandler(
            next_question_handler, pattern="^next$"
        ))
        # Stats callback handlers
        self.application.add_handler(CallbackQueryHandler(
            stats_back_callback, pattern="^stats:back$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            topic_stats_callback, pattern="^stats:"
        ))

        logger.info("Handlers registered successfully")

    async def _set_bot_commands(self) -> None:
        """Set bot commands menu for Telegram."""
        commands = [
            BotCommand(command="start", description="Initialize bot and register"),
            BotCommand(command="help", description="Show all commands"),
            BotCommand(command="topics", description="View available learning topics"),
            BotCommand(command="quiz", description="Start a quiz session"),
            BotCommand(command="stats", description="Show your learning statistics"),
            BotCommand(command="cancel", description="Cancel current quiz session"),
        ]

        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands menu set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")

    async def start(self) -> None:
        """Start the bot with polling."""
        logger.info("Starting Telegram bot...")
        try:
            # Start scheduler if enabled
            if self.scheduler:
                self.scheduler.start()
                logger.info("Question generation scheduler started")

            # Initialize the application
            async with self.application:
                # Set bot commands menu
                await self._set_bot_commands()

                # Start polling
                logger.info("Bot is running. Press Ctrl+C to stop.")
                await self.application.start()
                await self.application.updater.start_polling(
                    allowed_updates=["message", "callback_query"]
                )

                # Keep running until stopped
                import asyncio
                while True:
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the bot gracefully."""
        logger.info("Stopping Telegram bot...")
        try:
            # Stop scheduler if running
            if self.scheduler:
                self.scheduler.stop()
                logger.info("Scheduler stopped")

            if self.application.updater.running:
                await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)

    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get active quiz session for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Session dictionary or None
        """
        return self.active_sessions.get(user_id)

    def create_session(self, user_id: int, topic_id: int, topic_name: str) -> Dict[str, Any]:
        """
        Create new quiz session for user.

        Args:
            user_id: Telegram user ID
            topic_id: Database topic ID
            topic_name: Topic name for display

        Returns:
            Created session dictionary
        """
        # Get topic configuration to retrieve questions_per_batch
        topic = self.repository.get_topic(topic_id)
        questions_per_batch = 10  # Default
        if topic and topic.config:
            questions_per_batch = topic.config.get('questions_per_batch', 10)

        session = {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "current_question": None,
            "questions_answered": 0,
            "correct_answers": 0,
            "start_time": None,
            "questions_per_batch": questions_per_batch
        }
        self.active_sessions[user_id] = session
        logger.info(f"Created quiz session for user {user_id}, topic: {topic_name}, batch size: {questions_per_batch}")
        return session

    def end_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        End quiz session for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Final session data or None
        """
        session = self.active_sessions.pop(user_id, None)
        if session:
            logger.info(f"Ended quiz session for user {user_id}")
        return session
