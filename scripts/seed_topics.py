"""Script to seed topics from config files into the database."""

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


def seed_topics() -> None:
    """Seed topics from YAML configuration into database."""
    try:
        # Initialize database
        db_url = os.getenv('DATABASE_URL', 'sqlite:///learning_bot.db')
        repository = Repository(db_url)
        repository.create_tables()
        logger.info(f"Connected to database: {db_url}")

        # Load config
        config_dir = os.getenv('CONFIG_DIR', 'config')
        config_loader = ConfigLoader(config_dir)
        config_loader.load_all()

        # Get all topics from config
        topics_config = config_loader.topics

        if not topics_config:
            logger.error("No topics found in configuration")
            return

        logger.info(f"Found {len(topics_config)} topics in configuration")

        # Seed each topic
        for topic_id, topic_config in topics_config.items():
            topic_name = topic_config.name
            topic_type = topic_config.type

            # Convert TopicConfig to dict for storage (use __dict__)
            config_dict = topic_config.__dict__.copy()
            config_dict['id'] = topic_id  # Add the topic ID

            # Check if topic already exists
            existing_topics = repository.get_all_topics(active_only=False)
            existing_topic = next((t for t in existing_topics if t.name == topic_name), None)

            if existing_topic:
                logger.info(f"Topic already exists: {topic_name} (ID: {existing_topic.id})")
                # Update config if needed
                repository.update_topic(
                    topic_id=existing_topic.id,
                    config=config_dict,
                    is_active=True
                )
                logger.info(f"Updated topic configuration: {topic_name}")
            else:
                # Create new topic
                topic = repository.create_topic(
                    name=topic_name,
                    type=topic_type,
                    config=config_dict,
                    is_active=True
                )
                logger.info(f"Created new topic: {topic_name} (ID: {topic.id})")

        logger.info("Topic seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding topics: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    seed_topics()
