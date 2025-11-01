"""Manual question generation script for Telegram Learning Bot.

This script allows you to manually generate questions without enabling the scheduler.
Requires OPENROUTER_API_KEY to be set in .env file.

Usage:
    python scripts/generate_questions.py              # Generate 5 questions per topic
    python scripts/generate_questions.py --count 10   # Generate 10 questions per topic
    python scripts/generate_questions.py --topic 1    # Generate for specific topic ID
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.database.repository import Repository
from src.utils.config_loader import ConfigLoader
from src.services.llm_service import LLMService
from src.services.question_generator import QuestionGenerator
from src.services.example_parser import ExampleParser
from src.services.scheduler import QuestionScheduler
from src.utils.logger import setup_logger, get_logger

# Load environment
load_dotenv()

# Setup logger
setup_logger(log_level='INFO')
logger = get_logger(__name__)


async def generate_questions(topic_id: int = None, count: int = 5) -> int:
    """
    Generate questions manually.

    Args:
        topic_id: Optional specific topic ID (None = all topics)
        count: Number of questions to generate per topic

    Returns:
        Total number of questions generated
    """
    try:
        # Check for API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in .env file!")
            logger.error("Please add your OpenRouter API key to continue.")
            logger.error("Get one at: https://openrouter.ai/keys")
            return 0

        logger.info("=" * 60)
        logger.info("MANUAL QUESTION GENERATION")
        logger.info("=" * 60)

        # Initialize database
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./learning_bot.db')
        repository = Repository(db_url)
        logger.info(f"Connected to database: {db_url}")

        # Show available topics
        all_topics = repository.get_all_topics(active_only=True)
        if not all_topics:
            logger.error("No active topics found in database!")
            logger.error("Run: python scripts/seed_topics.py")
            return 0

        logger.info(f"Available topics in database:")
        for topic in all_topics:
            logger.info(f"  - ID {topic.id}: {topic.name}")
        logger.info("")

        # Validate topic_id if provided
        if topic_id:
            topic = repository.get_topic(topic_id)
            if not topic:
                logger.error(f"Topic ID {topic_id} not found!")
                logger.error(f"Available topic IDs: {', '.join(str(t.id) for t in all_topics)}")
                return 0
            if not topic.is_active:
                logger.error(f"Topic ID {topic_id} is not active!")
                return 0

        # Initialize config loader
        config_dir = os.getenv('CONFIG_DIR', 'config')
        config_loader = ConfigLoader(config_dir)
        config_loader.load_all()
        logger.info(f"Loaded configuration from: {config_dir}")

        # Initialize LLM service
        model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        llm_service = LLMService(api_key, model)
        logger.info(f"Using LLM model: {model}")

        # Initialize question generator
        example_parser = ExampleParser()
        question_generator = QuestionGenerator(llm_service, config_loader, example_parser, repository)

        # Initialize scheduler (for manual generation)
        scheduler = QuestionScheduler(repository, question_generator, config_loader)

        # Generate questions
        logger.info("")
        if topic_id:
            topic_name = repository.get_topic(topic_id).name
            logger.info(f"Generating {count} questions for topic ID {topic_id}: {topic_name}")
        else:
            logger.info(f"Generating {count} questions per topic (all {len(all_topics)} active topics)")

        logger.info("")
        logger.info("Starting generation... (this may take 30-60 seconds per topic)")
        logger.info("")

        total_generated = await scheduler.run_manual_generation(
            topic_id=topic_id,
            count=count
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✓ Generation complete!")
        logger.info(f"✓ Total questions generated: {total_generated}")
        logger.info("=" * 60)

        if total_generated > 0:
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Run diagnostics: python scripts/diagnose_database.py")
            logger.info("2. Start/restart your bot: python main.py")
            logger.info("3. Test in Telegram: Send /topics and select a topic")

        return total_generated

    except Exception as e:
        logger.error(f"Error generating questions: {e}", exc_info=True)
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Manually generate questions for Telegram Learning Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_questions.py                    # Generate 5 questions per topic
  python scripts/generate_questions.py --count 10         # Generate 10 per topic
  python scripts/generate_questions.py --topic 1          # Generate for topic ID 1
  python scripts/generate_questions.py --count 20 --topic 2  # Generate 20 for topic 2

Requirements:
  - OPENROUTER_API_KEY must be set in .env file
  - Topics must be seeded (run: python scripts/seed_topics.py)
  - Get API key at: https://openrouter.ai/keys
        """
    )

    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of questions to generate per topic (default: 5)'
    )

    parser.add_argument(
        '--topic',
        type=int,
        default=None,
        help='Specific topic ID to generate for (default: all topics)'
    )

    args = parser.parse_args()

    # Validate count
    if args.count < 1 or args.count > 50:
        logger.error("Count must be between 1 and 50")
        sys.exit(1)

    # Run generation
    try:
        total = asyncio.run(generate_questions(
            topic_id=args.topic,
            count=args.count
        ))

        if total == 0:
            logger.error("No questions were generated. Check logs for errors.")
            sys.exit(1)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("\nGeneration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
