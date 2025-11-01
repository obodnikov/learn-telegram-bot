"""Convenience script for exporting database topics to YAML.

This is a simple wrapper around manage_topics.py export command.

Usage:
    python scripts/export_topics.py                           # Export with timestamp filename
    python scripts/export_topics.py topics_backup.yaml        # Export to specific file
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.database.repository import Repository
from src.utils.logger import setup_logger, get_logger

# Load environment
load_dotenv()

# Setup logger
setup_logger(log_level='INFO')
logger = get_logger(__name__)


def main():
    """Main entry point."""
    # Get output file from command line if provided
    output_file = sys.argv[1] if len(sys.argv) > 1 else None

    logger.info("=" * 80)
    logger.info("EXPORT TOPICS - Database to YAML")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Initialize database
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./learning_bot.db')
        repository = Repository(db_url)
        logger.info(f"Connected to database: {db_url}")
        logger.info("")

        # Import export function from manage_topics
        from scripts.manage_topics import export_topics

        # Run export
        export_topics(repository, output_file=output_file)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error during export: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
