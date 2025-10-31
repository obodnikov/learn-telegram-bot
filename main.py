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

    try:
        repository = Repository(db_url)
        repository.create_tables()
        logger.info("Database initialized successfully")
        return repository
    except Exception as e:
        raise DatabaseError(f"Database initialization failed: {e}")


def main() -> None:
    """
    Main application entry point.

    Performs startup validation and initializes the bot.
    """
    try:
        logger.info("Starting Telegram Learning Bot...")

        # Run startup validation
        config_dir = os.getenv('CONFIG_DIR', 'config')
        validator = StartupValidator(config_dir)
        validator.run_startup_checks()

        # Initialize database
        repository = initialize_database()
        logger.info("Phase 2 components initialized: Database & Repository")

        # TODO: Phase 3 - Initialize LLM service
        # api_key = os.getenv('OPENROUTER_API_KEY')
        # model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        # llm_service = LLMService(api_key, model)

        # TODO: Phase 4 - Initialize bot and start polling
        logger.info("Bot initialization complete (Phase 2)")
        logger.info("Database ready, LLM integration available")
        logger.info("Ready for Phase 3 implementation (Telegram bot handlers)")

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
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
