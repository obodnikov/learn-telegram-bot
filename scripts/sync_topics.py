"""Convenience script for syncing topics from YAML to database.

This is a simple wrapper around manage_topics.py sync command.

Usage:
    python scripts/sync_topics.py              # Sync topics
    python scripts/sync_topics.py --dry-run    # Preview changes without applying
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.database.repository import Repository
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger, get_logger

# Load environment
load_dotenv()

# Setup logger
setup_logger(log_level='INFO')
logger = get_logger(__name__)


def main():
    """Main entry point."""
    dry_run = '--dry-run' in sys.argv

    logger.info("=" * 80)
    logger.info("TOPIC SYNC - YAML to Database")
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Initialize database
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./learning_bot.db')
        repository = Repository(db_url)
        logger.info(f"Connected to database: {db_url}")

        # Initialize config loader
        config_dir = os.getenv('CONFIG_DIR', 'config')
        config_loader = ConfigLoader(config_dir)
        logger.info(f"Loading topics from: {config_dir}/topics.yaml")
        logger.info("")

        # Import sync function from manage_topics
        from scripts.manage_topics import sync_topics

        # Run sync
        sync_topics(config_loader, repository, dry_run=dry_run)

        if dry_run:
            logger.info("")
            logger.info("To apply these changes, run:")
            logger.info("  python scripts/sync_topics.py")

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
