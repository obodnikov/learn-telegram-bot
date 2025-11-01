"""Main entry point for the Telegram Learning Bot."""
import os
import sys
from dotenv import load_dotenv
from src.utils.logger import setup_logger, get_logger
from src.core.startup import StartupValidator
from src.utils.exceptions import ConfigurationError, DatabaseError
from src.database.repository import Repository

# Load environment variables
load_dotenv()

# Setup logger
setup_logger(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', 'logs/bot.log')
)

logger = get_logger(__name__)


def initialize_database() -> Repository:
    """
    Initialize database and create tables.

    Returns:
        Repository instance

    Raises:
        DatabaseError: If database initialization fails
    """
    db_url = os.getenv('DATABASE_URL', 'sqlite:///learning_bot.db')
    logger.info(f"Initializing database: {db_url}")

    # Log absolute path for SQLite databases
    if db_url.startswith('sqlite:///'):
        import os.path
        db_path = db_url.replace('sqlite:///', '')
        abs_path = os.path.abspath(db_path)
        logger.info(f"Database absolute path: {abs_path}")
        logger.info(f"Database file exists: {os.path.exists(abs_path)}")

    try:
        repository = Repository(db_url)
        repository.create_tables()

        # Log topic count on startup
        topics = repository.get_all_topics(active_only=False)
        logger.info(f"Database initialized successfully - found {len(topics)} topics in database")
        for topic in topics:
            logger.info(f"  Topic: {topic.name} (Active: {topic.is_active})")

        return repository
    except Exception as e:
        raise DatabaseError(f"Database initialization failed: {e}")


async def main_async() -> None:
    """
    Main application entry point (async).

    Performs startup validation and initializes the bot.
    """
    bot = None
    try:
        logger.info("Starting Telegram Learning Bot...")

        # Run startup validation
        config_dir = os.getenv('CONFIG_DIR', 'config')
        validator = StartupValidator(config_dir)
        validator.run_startup_checks()

        # Initialize database
        repository = initialize_database()
        logger.info("Phase 2 components initialized: Database & Repository")

        # Initialize config loader
        from src.utils.config_loader import ConfigLoader
        config_loader = ConfigLoader(config_dir)
        config_loader.load_all()

        # Initialize LLM service (optional)
        llm_service = None
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            from src.services.llm_service import LLMService
            model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
            llm_service = LLMService(api_key, model)
            logger.info("LLM service initialized")
        else:
            logger.warning("OPENROUTER_API_KEY not set, LLM features disabled")

        # Initialize and start bot
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN not set in environment")

        # Check if scheduler should be enabled
        enable_scheduler = os.getenv('ENABLE_SCHEDULER', 'false').lower() == 'true'
        if enable_scheduler and not llm_service:
            logger.warning("Scheduler enabled but LLM service not available. Disabling scheduler.")
            enable_scheduler = False

        from src.bot import LearningBot
        bot = LearningBot(token, repository, config_loader, llm_service, enable_scheduler)

        logger.info("All components initialized successfully")
        if enable_scheduler:
            logger.info("Question generation scheduler is enabled")
        logger.info("Starting Telegram bot...")

        # Start the bot
        await bot.start()

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please fix configuration issues and restart the bot")
        sys.exit(1)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        logger.error("Please check database configuration and try again")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
        if bot:
            await bot.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        if bot:
            await bot.stop()
        sys.exit(1)


def main() -> None:
    """Wrapper to run async main."""
    import asyncio
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
