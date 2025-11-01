"""Diagnostic script to check database status and topics."""
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


def diagnose():
    """Run database diagnostics."""
    logger.info("=" * 60)
    logger.info("DATABASE DIAGNOSTIC TOOL")
    logger.info("=" * 60)

    # Check environment
    db_url = os.getenv('DATABASE_URL', 'sqlite:///learning_bot.db')
    logger.info(f"\n1. Environment Configuration:")
    logger.info(f"   DATABASE_URL: {db_url}")

    # Check file paths for SQLite
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        abs_path = os.path.abspath(db_path)

        logger.info(f"\n2. File System:")
        logger.info(f"   Relative path: {db_path}")
        logger.info(f"   Absolute path: {abs_path}")
        logger.info(f"   File exists: {os.path.exists(abs_path)}")

        if os.path.exists(abs_path):
            file_size = os.path.getsize(abs_path)
            logger.info(f"   File size: {file_size} bytes")

    # Connect to database
    logger.info(f"\n3. Database Connection:")
    try:
        repository = Repository(db_url)
        logger.info(f"   ✓ Connected successfully")

        # Query topics
        logger.info(f"\n4. Topics in Database:")
        all_topics = repository.get_all_topics(active_only=False)
        logger.info(f"   Total topics: {len(all_topics)}")

        if all_topics:
            for topic in all_topics:
                status = "ACTIVE" if topic.is_active else "INACTIVE"
                logger.info(f"   - [{status}] {topic.name} (ID: {topic.id})")
        else:
            logger.warning("   ⚠️  No topics found in database!")
            logger.warning("   Run: python scripts/seed_topics.py")

        # Query active topics specifically
        active_topics = repository.get_all_topics(active_only=True)
        logger.info(f"\n5. Active Topics:")
        logger.info(f"   Count: {len(active_topics)}")

        if not active_topics and all_topics:
            logger.warning("   ⚠️  Topics exist but none are active!")

        # Query questions
        from src.database.models import Question
        with repository.get_session() as session:
            question_count = session.query(Question).count()

        logger.info(f"\n6. Questions in Database:")
        logger.info(f"   Total questions: {question_count}")

        if question_count == 0:
            logger.warning("   ⚠️  No questions generated yet!")
            logger.info("   Note: Topics will still be visible even without questions")

        # Summary
        logger.info(f"\n" + "=" * 60)
        if active_topics:
            logger.info(f"✅ DIAGNOSIS: Database is healthy!")
            logger.info(f"   {len(active_topics)} active topics available")
            logger.info(f"   Bot should work correctly")
        elif all_topics:
            logger.error(f"❌ DIAGNOSIS: Topics exist but are INACTIVE!")
            logger.info(f"   Run: python scripts/seed_topics.py")
        else:
            logger.error(f"❌ DIAGNOSIS: No topics in database!")
            logger.info(f"   Run: python scripts/seed_topics.py")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"   ✗ Connection failed: {e}")
        logger.error(f"\n❌ DIAGNOSIS: Cannot connect to database!")
        return False

    return True


if __name__ == "__main__":
    try:
        success = diagnose()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Diagnostic error: {e}", exc_info=True)
        sys.exit(1)
