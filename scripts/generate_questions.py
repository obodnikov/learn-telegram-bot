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


async def generate_questions(
    topic_id: int = None,
    count: int = 5,
    similarity_threshold: float = 0.85,
    duplicate_retry_threshold: float = 0.50,
    max_retries: int = 3,
    recent_context: int = 20,
    use_enhanced: bool = False
) -> int:
    """
    Generate questions manually.

    Args:
        topic_id: Optional specific topic ID (None = all topics)
        count: Number of questions to generate per topic
        similarity_threshold: Reject if similarity > threshold (0.0-1.0)
        duplicate_retry_threshold: Retry if duplicates > threshold (0.0-1.0)
        max_retries: Maximum retry attempts
        recent_context: Number of recent questions for LLM context
        use_enhanced: Use enhanced generation with duplicate detection

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

        # Generate questions
        logger.info("")
        if topic_id:
            topic_name = repository.get_topic(topic_id).name
            logger.info(f"Generating {count} questions for topic ID {topic_id}: {topic_name}")
        else:
            logger.info(f"Generating {count} questions per topic (all {len(all_topics)} active topics)")

        if use_enhanced:
            logger.info(f"Using ENHANCED generation with duplicate detection:")
            logger.info(f"  - Similarity threshold: {similarity_threshold}")
            logger.info(f"  - Duplicate retry threshold: {duplicate_retry_threshold}%")
            logger.info(f"  - Max retries: {max_retries}")
            logger.info(f"  - Recent context size: {recent_context}")
        else:
            logger.info(f"Using STANDARD generation (add --enhanced for duplicate detection)")

        logger.info("")
        logger.info("Starting generation... (this may take 30-60 seconds per topic)")
        logger.info("")

        # Determine which topics to process
        topics_to_process = [all_topics[topic_id - 1]] if topic_id else all_topics
        total_generated = 0

        for topic in topics_to_process:
            logger.info(f"\nGenerating questions for: {topic.name}")

            # Get YAML topic ID from config
            yaml_topic_id = None
            for yaml_id, yaml_config in config_loader.topics.items():
                if yaml_config.name == topic.name:
                    yaml_topic_id = yaml_id
                    break

            if not yaml_topic_id:
                logger.warning(f"Could not find YAML config for topic: {topic.name}")
                continue

            try:
                if use_enhanced:
                    # Use enhanced generation with duplicate detection
                    questions = await question_generator.generate_questions_with_dedup(
                        topic_id=yaml_topic_id,
                        count=count,
                        db_topic_id=topic.id,
                        similarity_threshold=similarity_threshold,
                        duplicate_retry_threshold=duplicate_retry_threshold,
                        max_retries=max_retries,
                        recent_context_limit=recent_context
                    )
                else:
                    # Use standard generation
                    questions = await question_generator.generate_questions(
                        topic_id=yaml_topic_id,
                        count=count,
                        db_topic_id=topic.id
                    )

                # Save questions to database
                saved_count = 0
                for question_data in questions:
                    question_data['topic_id'] = topic.id
                    repository.create_question(question_data)
                    saved_count += 1

                logger.info(f"✓ Saved {saved_count} questions for {topic.name}")
                total_generated += saved_count

            except Exception as e:
                logger.error(f"Error generating questions for {topic.name}: {e}")

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
  # Standard generation
  python scripts/generate_questions.py                    # Generate 5 questions per topic
  python scripts/generate_questions.py --count 10         # Generate 10 per topic
  python scripts/generate_questions.py --topic 1          # Generate for topic ID 1

  # Enhanced generation with duplicate detection
  python scripts/generate_questions.py --enhanced         # Use fuzzy duplicate detection
  python scripts/generate_questions.py --enhanced --count 10 --topic 1
  python scripts/generate_questions.py --enhanced --similarity-threshold 0.90
  python scripts/generate_questions.py --enhanced --duplicate-retry-threshold 0.40 --max-retries 5

Duplicate Detection Parameters (--enhanced mode):
  --similarity-threshold      Reject if similarity > threshold (default: 0.85)
  --duplicate-retry-threshold Retry if duplicates > threshold (default: 0.50)
  --max-retries              Maximum retry attempts (default: 3)
  --recent-context           Recent questions for LLM context (default: 20)

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

    parser.add_argument(
        '--enhanced',
        action='store_true',
        help='Use enhanced generation with fuzzy duplicate detection and retry logic'
    )

    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.85,
        help='Similarity threshold for duplicate detection, 0.0-1.0 (default: 0.85)'
    )

    parser.add_argument(
        '--duplicate-retry-threshold',
        type=float,
        default=0.50,
        help='Retry if duplicate rate exceeds this threshold, 0.0-1.0 (default: 0.50)'
    )

    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts when duplicates exceed threshold (default: 3)'
    )

    parser.add_argument(
        '--recent-context',
        type=int,
        default=20,
        help='Number of recent questions to show LLM as context (default: 20)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.count < 1 or args.count > 50:
        logger.error("Count must be between 1 and 50")
        sys.exit(1)

    if not (0.0 <= args.similarity_threshold <= 1.0):
        logger.error("Similarity threshold must be between 0.0 and 1.0")
        sys.exit(1)

    if not (0.0 <= args.duplicate_retry_threshold <= 1.0):
        logger.error("Duplicate retry threshold must be between 0.0 and 1.0")
        sys.exit(1)

    if args.max_retries < 0 or args.max_retries > 10:
        logger.error("Max retries must be between 0 and 10")
        sys.exit(1)

    if args.recent_context < 0 or args.recent_context > 100:
        logger.error("Recent context must be between 0 and 100")
        sys.exit(1)

    # Run generation
    try:
        total = asyncio.run(generate_questions(
            topic_id=args.topic,
            count=args.count,
            similarity_threshold=args.similarity_threshold,
            duplicate_retry_threshold=args.duplicate_retry_threshold,
            max_retries=args.max_retries,
            recent_context=args.recent_context,
            use_enhanced=args.enhanced
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
