"""Main entry point for the Telegram Learning Bot."""
import os
import sys
from dotenv import load_dotenv
from src.utils.logger import setup_logger, get_logger
from src.core.startup import StartupValidator
from src.utils.exceptions import ConfigurationError

# Load environment variables
load_dotenv()

# Setup logger
setup_logger(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', 'logs/bot.log')
)

logger = get_logger(__name__)


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
        
        # TODO: Initialize bot and start polling
        logger.info("Bot initialization complete (Phase 1 - validation only)")
        logger.info("Ready for Phase 2 implementation (database and LLM integration)")
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please fix configuration issues and restart the bot")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
