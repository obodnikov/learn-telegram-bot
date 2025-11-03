"""Question management script for Telegram Learning Bot.

This script provides tools for managing questions in the database:
- Export questions to JSON
- Import questions from JSON
- Delete questions by ID
- Remove last N questions
- Show question details
- List questions with filters

Usage:
    python scripts/manage_questions.py export --topic 1
    python scripts/manage_questions.py delete --id 42
    python scripts/manage_questions.py remove-last --count 5 --topic 1
    python scripts/manage_questions.py show --id 42
    python scripts/manage_questions.py list --topic 1
    python scripts/manage_questions.py import --file questions.json --topic 1
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import desc
from src.database.repository import Repository
from src.database.models import Question, Topic
from src.utils.logger import setup_logger, get_logger

# Load environment
load_dotenv()

# Setup logger
setup_logger(log_level='INFO')
logger = get_logger(__name__)


def export_questions(repository: Repository, topic_id: Optional[int] = None, output_file: Optional[str] = None) -> str:
    """
    Export questions to JSON file.

    Args:
        repository: Database repository
        topic_id: Optional topic ID filter
        output_file: Optional output file path

    Returns:
        Path to exported file
    """
    # Build query
    if topic_id:
        topic = repository.get_topic(topic_id)
        if not topic:
            logger.error(f"Topic ID {topic_id} not found")
            sys.exit(1)

        with repository.get_session() as session:
            questions = session.query(Question).filter(
                Question.topic_id == topic_id
            ).order_by(Question.created_at).all()

        topic_name = topic.name.replace(' ', '_').replace('-', '_').lower()
        default_filename = f"questions_{topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        with repository.get_session() as session:
            questions = session.query(Question).order_by(
                Question.topic_id, Question.created_at
            ).all()
        default_filename = f"questions_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    if not questions:
        logger.warning("No questions found to export")
        return ""

    # Convert to JSON format (without metadata)
    questions_data = []
    for q in questions:
        questions_data.append({
            "question_text": q.question_text,
            "choice_a": q.choice_a,
            "choice_b": q.choice_b,
            "choice_c": q.choice_c,
            "choice_d": q.choice_d,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "tags": q.tags
        })

    # Determine output file
    output_path = output_file or default_filename

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✓ Exported {len(questions_data)} questions to: {output_path}")
    return output_path


def import_questions(repository: Repository, file_path: str, topic_id: int, force: bool = False) -> int:
    """
    Import questions from JSON file.

    Args:
        repository: Database repository
        file_path: Path to JSON file
        topic_id: Topic ID to assign questions to
        force: Skip confirmation

    Returns:
        Number of questions imported
    """
    # Verify topic exists
    topic = repository.get_topic(topic_id)
    if not topic:
        logger.error(f"Topic ID {topic_id} not found")
        sys.exit(1)

    # Load JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)

    if not isinstance(questions_data, list):
        logger.error("JSON file must contain an array of questions")
        sys.exit(1)

    logger.info(f"Found {len(questions_data)} questions in file")
    logger.info(f"Target topic: {topic.name} (ID: {topic_id})")

    # Check for duplicates
    with repository.get_session() as session:
        existing_questions = session.query(Question).filter(
            Question.topic_id == topic_id
        ).all()
        existing_texts = {q.question_text for q in existing_questions}

    new_questions = []
    duplicate_questions = []

    for q_data in questions_data:
        if q_data.get('question_text') in existing_texts:
            duplicate_questions.append(q_data['question_text'][:50] + '...')
        else:
            new_questions.append(q_data)

    logger.info(f"New questions to import: {len(new_questions)}")
    logger.info(f"Duplicate questions (will skip): {len(duplicate_questions)}")

    if not new_questions:
        logger.warning("No new questions to import")
        return 0

    # Confirmation
    if not force:
        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  - File: {file_path}")
        print(f"  - Topic: {topic.name}")
        print(f"  - New questions: {len(new_questions)}")
        print(f"  - Duplicates (skip): {len(duplicate_questions)}")
        print(f"{'='*60}\n")

        response = input("Proceed with import? (yes/no): ").strip().lower()
        if response != 'yes':
            logger.info("Import cancelled")
            return 0

    # Import questions
    imported_count = 0
    for q_data in new_questions:
        try:
            # Validate required fields
            required_fields = ['question_text', 'choice_a', 'choice_b', 'choice_c', 'choice_d',
                             'correct_answer', 'explanation', 'difficulty']
            missing_fields = [f for f in required_fields if f not in q_data]

            if missing_fields:
                logger.warning(f"Skipping question with missing fields: {missing_fields}")
                continue

            # Add to database
            q_data['topic_id'] = topic_id
            if 'tags' not in q_data:
                q_data['tags'] = []
            if 'source' not in q_data:
                q_data['source'] = 'file'

            repository.create_question(q_data)
            imported_count += 1

        except Exception as e:
            logger.error(f"Error importing question: {e}")
            continue

    logger.info(f"✓ Successfully imported {imported_count} questions")
    return imported_count


def delete_question(repository: Repository, question_id: int, force: bool = False) -> bool:
    """
    Delete a question by ID.

    Args:
        repository: Database repository
        question_id: Question ID to delete
        force: Skip confirmation

    Returns:
        True if deleted, False otherwise
    """
    # Get question
    with repository.get_session() as session:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            logger.error(f"Question ID {question_id} not found")
            return False

        # Get topic name
        topic = repository.get_topic(question.topic_id)
        topic_name = topic.name if topic else "Unknown"

        # Count related data
        progress_count = len(question.progress)
        has_analytics = question.analytics is not None

        # Store question details before session closes
        question_details = {
            'id': question.id,
            'question_text': question.question_text,
            'choice_a': question.choice_a,
            'choice_b': question.choice_b,
            'choice_c': question.choice_c,
            'choice_d': question.choice_d,
            'correct_answer': question.correct_answer,
            'difficulty': question.difficulty,
            'created_at': question.created_at
        }

    # Show question details
    print(f"\n{'='*60}")
    print(f"WARNING: You are about to delete question ID {question_id}")
    print(f"{'='*60}")
    print(f"\nQuestion ID: {question_details['id']}")
    print(f"Topic: {topic_name}")
    print(f"Difficulty: {question_details['difficulty']}")
    print(f"Created: {question_details['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nQuestion: {question_details['question_text']}")
    print(f"  A) {question_details['choice_a']}")
    print(f"  B) {question_details['choice_b']}")
    print(f"  C) {question_details['choice_c']}")
    print(f"  D) {question_details['choice_d']}")
    print(f"  ✓ Correct answer: {question_details['correct_answer']}")

    print(f"\nThis will also delete:")
    if progress_count > 0:
        print(f"  - User progress data ({progress_count} users have answered this question)")
    else:
        print(f"  - User progress data (no users have answered this question yet)")

    if has_analytics:
        print(f"  - Question analytics data")

    print(f"\n{'='*60}\n")

    # Confirmation
    if not force:
        response = input("Type 'yes' to confirm deletion: ").strip().lower()
        if response != 'yes':
            logger.info("Deletion cancelled")
            return False

    # Delete question (CASCADE will handle related data)
    try:
        with repository.get_session() as session:
            question = session.query(Question).filter(Question.id == question_id).first()
            if question:
                session.delete(question)
                session.commit()
        logger.info(f"✓ Question ID {question_id} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        return False


def remove_last_questions(repository: Repository, count: int, topic_id: Optional[int] = None, force: bool = False) -> int:
    """
    Remove last N questions.

    Args:
        repository: Database repository
        count: Number of questions to remove
        topic_id: Optional topic ID filter
        force: Skip confirmation

    Returns:
        Number of questions deleted
    """
    # Build query and get questions
    with repository.get_session() as session:
        query = session.query(Question)

        if topic_id:
            topic = repository.get_topic(topic_id)
            if not topic:
                logger.error(f"Topic ID {topic_id} not found")
                sys.exit(1)
            query = query.filter(Question.topic_id == topic_id)
            topic_desc = f" from topic '{topic.name}'"
        else:
            topic_desc = ""

        # Get last N questions (ordered by ID, descending)
        questions = query.order_by(desc(Question.id)).limit(count).all()

        if not questions:
            logger.warning(f"No questions found{topic_desc}")
            return 0

        # Store question details before session closes
        question_summaries = [
            {'id': q.id, 'text': q.question_text[:60] + '...'}
            for q in questions
        ]
        question_ids = [q.id for q in questions]

    # Show summary
    print(f"\n{'='*60}")
    print(f"WARNING: About to delete {len(question_summaries)} question(s){topic_desc}")
    print(f"{'='*60}")
    print(f"\nQuestion IDs: {', '.join(str(qid) for qid in question_ids)}")
    print(f"\nThis will delete:")

    for q in question_summaries:
        print(f"  - ID {q['id']}: {q['text']}")

    print(f"\nAll related user progress and analytics data will also be deleted.")
    print(f"{'='*60}\n")

    # Confirmation
    if not force:
        response = input(f"Type 'yes' to confirm deletion of {len(question_summaries)} question(s): ").strip().lower()
        if response != 'yes':
            logger.info("Deletion cancelled")
            return 0

    # Delete questions
    try:
        with repository.get_session() as session:
            for question_id in question_ids:
                question = session.query(Question).filter(Question.id == question_id).first()
                if question:
                    session.delete(question)
            session.commit()
        logger.info(f"✓ Successfully deleted {len(question_ids)} question(s)")
        return len(question_ids)
    except Exception as e:
        logger.error(f"Error deleting questions: {e}")
        return 0


def show_question(repository: Repository, question_id: int) -> None:
    """
    Show question details.

    Args:
        repository: Database repository
        question_id: Question ID to show
    """
    # Get question
    with repository.get_session() as session:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            logger.error(f"Question ID {question_id} not found")
            return

        # Get topic name
        topic = repository.get_topic(question.topic_id)
        topic_name = topic.name if topic else "Unknown"

        # Store all data before session closes
        q_data = {
            'id': question.id,
            'question_text': question.question_text,
            'choice_a': question.choice_a,
            'choice_b': question.choice_b,
            'choice_c': question.choice_c,
            'choice_d': question.choice_d,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'difficulty': question.difficulty,
            'created_at': question.created_at,
            'tags': question.tags,
            'source': question.source,
            'source_file': question.source_file,
            'progress_count': len(question.progress)
        }

        # Get analytics if available
        if question.analytics:
            q_data['analytics'] = {
                'total_times_shown': question.analytics.total_times_shown,
                'total_correct': question.analytics.total_correct,
                'total_incorrect': question.analytics.total_incorrect,
                'success_rate': question.analytics.success_rate
            }
        else:
            q_data['analytics'] = None

    # Display question
    print(f"\n{'='*60}")
    print(f"Question ID: {q_data['id']}")
    print(f"Topic: {topic_name}")
    print(f"Difficulty: {q_data['difficulty']}")
    print(f"Created: {q_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nQuestion: {q_data['question_text']}")
    print(f"  A) {q_data['choice_a']}")
    print(f"  B) {q_data['choice_b']}")
    print(f"  C) {q_data['choice_c']}")
    print(f"  D) {q_data['choice_d']}")
    print(f"\n  ✓ Correct answer: {q_data['correct_answer']}")
    print(f"\nExplanation:\n{q_data['explanation']}")

    if q_data['tags']:
        print(f"\nTags: {', '.join(q_data['tags'])}")

    print(f"\nSource: {q_data['source']}")
    if q_data['source_file']:
        print(f"Source file: {q_data['source_file']}")

    # Show statistics if available
    if q_data['analytics']:
        print(f"\nStatistics:")
        print(f"  - Times shown: {q_data['analytics']['total_times_shown']}")
        print(f"  - Correct: {q_data['analytics']['total_correct']}")
        print(f"  - Incorrect: {q_data['analytics']['total_incorrect']}")
        if q_data['analytics']['total_times_shown'] > 0:
            success_rate = q_data['analytics']['success_rate'] * 100
            print(f"  - Success rate: {success_rate:.1f}%")

    # Show user progress count
    if q_data['progress_count'] > 0:
        print(f"\nUser Progress:")
        print(f"  - {q_data['progress_count']} user(s) have answered this question")

    print(f"{'='*60}\n")


def list_questions(repository: Repository, topic_id: Optional[int] = None, difficulty: Optional[str] = None, limit: int = 50) -> None:
    """
    List questions with filters.

    Args:
        repository: Database repository
        topic_id: Optional topic ID filter
        difficulty: Optional difficulty filter
        limit: Maximum number of questions to show
    """
    # Build query and get questions
    with repository.get_session() as session:
        query = session.query(Question)

        filters = []
        if topic_id:
            topic = repository.get_topic(topic_id)
            if not topic:
                logger.error(f"Topic ID {topic_id} not found")
                sys.exit(1)
            query = query.filter(Question.topic_id == topic_id)
            filters.append(f"topic: {topic.name}")

        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
            filters.append(f"difficulty: {difficulty}")

        # Get total count before limit
        total_count = query.count()

        # Get questions
        questions = query.order_by(desc(Question.id)).limit(limit).all()

        if not questions:
            logger.warning("No questions found")
            return

        # Store question data before session closes
        question_list = []
        for q in questions:
            topic = repository.get_topic(q.topic_id)
            topic_name = topic.name if topic else "Unknown"
            question_preview = q.question_text[:50] + '...' if len(q.question_text) > 50 else q.question_text
            question_list.append({
                'id': q.id,
                'topic_name': topic_name,
                'difficulty': q.difficulty,
                'preview': question_preview
            })

    # Show header
    filter_str = f" ({', '.join(filters)})" if filters else ""
    print(f"\n{'='*60}")
    print(f"Questions{filter_str}")
    print(f"Showing {len(question_list)} of {total_count} total")
    print(f"{'='*60}\n")

    # Show questions
    for q in question_list:
        print(f"ID {q['id']:4d} | {q['topic_name']:30s} | {q['difficulty']:12s} | {q['preview']}")

    print(f"\n{'='*60}")
    print(f"Use 'python scripts/manage_questions.py show --id <ID>' to see details")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Question management tool for Telegram Learning Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export questions
  python scripts/manage_questions.py export                           # Export all questions
  python scripts/manage_questions.py export --topic 1                 # Export from topic 1
  python scripts/manage_questions.py export --topic 1 --output my.json  # Custom filename

  # Import questions
  python scripts/manage_questions.py import --file questions.json --topic 1
  python scripts/manage_questions.py import --file q.json --topic 1 --force  # Skip confirmation

  # Delete question
  python scripts/manage_questions.py delete --id 42                   # Delete question 42
  python scripts/manage_questions.py delete --id 42 --force           # Skip confirmation

  # Remove last N questions
  python scripts/manage_questions.py remove-last --count 5            # Remove last 5 (all topics)
  python scripts/manage_questions.py remove-last --count 5 --topic 1  # From topic 1
  python scripts/manage_questions.py remove-last --count 10 --force   # Skip confirmation

  # Show question
  python scripts/manage_questions.py show --id 42                     # Show details

  # List questions
  python scripts/manage_questions.py list                             # List all (limit 50)
  python scripts/manage_questions.py list --topic 1                   # From topic 1
  python scripts/manage_questions.py list --difficulty advanced       # By difficulty
  python scripts/manage_questions.py list --limit 100                 # Show more
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export questions to JSON')
    export_parser.add_argument('--topic', type=int, help='Topic ID to export from')
    export_parser.add_argument('--output', type=str, help='Output file path')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import questions from JSON')
    import_parser.add_argument('--file', required=True, type=str, help='JSON file to import')
    import_parser.add_argument('--topic', required=True, type=int, help='Topic ID to import to')
    import_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete question by ID')
    delete_parser.add_argument('--id', required=True, type=int, help='Question ID to delete')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    # Remove-last command
    remove_parser = subparsers.add_parser('remove-last', help='Remove last N questions')
    remove_parser.add_argument('--count', required=True, type=int, help='Number of questions to remove')
    remove_parser.add_argument('--topic', type=int, help='Topic ID to remove from')
    remove_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show question details')
    show_parser.add_argument('--id', required=True, type=int, help='Question ID to show')

    # List command
    list_parser = subparsers.add_parser('list', help='List questions')
    list_parser.add_argument('--topic', type=int, help='Filter by topic ID')
    list_parser.add_argument('--difficulty', type=str, help='Filter by difficulty')
    list_parser.add_argument('--limit', type=int, default=50, help='Maximum questions to show (default: 50)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./learning_bot.db')
    repository = Repository(db_url)
    logger.info(f"Connected to database: {db_url}")

    # Execute command
    try:
        if args.command == 'export':
            export_questions(repository, args.topic, args.output)

        elif args.command == 'import':
            import_questions(repository, args.file, args.topic, args.force)

        elif args.command == 'delete':
            delete_question(repository, args.id, args.force)

        elif args.command == 'remove-last':
            remove_last_questions(repository, args.count, args.topic, args.force)

        elif args.command == 'show':
            show_question(repository, args.id)

        elif args.command == 'list':
            list_questions(repository, args.topic, args.difficulty, args.limit)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
