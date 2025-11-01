"""Topic management CLI for Telegram Learning Bot.

This script provides commands to manage learning topics in the database.

Commands:
    list        - Show all topics with their current parameters
    sync        - Sync topics from YAML to database (add new, update existing, deactivate removed)
    delete      - Soft delete a topic (set is_active=False)
    activate    - Reactivate a deactivated topic
    export      - Export current database topics to YAML
    diff        - Show differences between YAML and database

Usage:
    python scripts/manage_topics.py list
    python scripts/manage_topics.py sync [--dry-run]
    python scripts/manage_topics.py delete <topic_id>
    python scripts/manage_topics.py activate <topic_id>
    python scripts/manage_topics.py export [--output topics_backup.yaml]
    python scripts/manage_topics.py diff
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

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


def list_topics(repository: Repository) -> None:
    """List all topics with their current parameters."""
    logger.info("=" * 80)
    logger.info("ALL TOPICS IN DATABASE")
    logger.info("=" * 80)

    topics = repository.get_all_topics(active_only=False)

    if not topics:
        logger.info("No topics found in database.")
        return

    for topic in topics:
        status = "ACTIVE" if topic.is_active else "INACTIVE"
        logger.info(f"\nTopic ID: {topic.id}")
        logger.info(f"  Name: {topic.name}")
        logger.info(f"  Type: {topic.type}")
        logger.info(f"  Status: {status}")
        logger.info(f"  Created: {topic.created_at}")

        # Show key config parameters
        config = topic.config
        if config:
            logger.info(f"  Config:")
            for key in ['questions_per_batch', 'difficulty', 'target_language', 'native_language']:
                if key in config:
                    logger.info(f"    {key}: {config[key]}")

        # Show question count
        questions = repository.get_questions_for_topic(topic.id)
        logger.info(f"  Questions: {len(questions)}")

    logger.info("\n" + "=" * 80)
    logger.info(f"Total topics: {len(topics)}")
    logger.info(f"Active: {sum(1 for t in topics if t.is_active)}")
    logger.info(f"Inactive: {sum(1 for t in topics if not t.is_active)}")
    logger.info("=" * 80)


def get_yaml_topics(config_loader: ConfigLoader) -> Dict[str, Any]:
    """Load topics from YAML configuration."""
    config_loader.load_all()
    # ConfigLoader stores topics in self.topics dictionary
    return config_loader.topics


def compare_topics(
    yaml_topics: Dict[str, Any],
    db_topics: List[Any]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Compare YAML topics with database topics.

    Returns:
        Tuple of (topics_to_add, topics_to_update, topics_to_deactivate)
    """
    yaml_names = {topic.name for topic_id, topic in yaml_topics.items()}
    db_topic_map = {topic.name: topic for topic in db_topics}
    db_names = set(db_topic_map.keys())

    topics_to_add = list(yaml_names - db_names)
    topics_to_update = list(yaml_names & db_names)
    topics_to_deactivate = list(db_names - yaml_names)

    return topics_to_add, topics_to_update, topics_to_deactivate


def show_diff(config_loader: ConfigLoader, repository: Repository) -> None:
    """Show differences between YAML and database."""
    logger.info("=" * 80)
    logger.info("YAML vs DATABASE DIFF")
    logger.info("=" * 80)

    yaml_topics = get_yaml_topics(config_loader)
    db_topics = repository.get_all_topics(active_only=False)

    to_add, to_update, to_deactivate = compare_topics(yaml_topics, db_topics)

    if to_add:
        logger.info(f"\n✓ Topics to ADD ({len(to_add)}):")
        for name in to_add:
            logger.info(f"  + {name}")

    if to_update:
        logger.info(f"\n↻ Topics to UPDATE ({len(to_update)}):")
        for name in to_update:
            logger.info(f"  ↻ {name}")

    if to_deactivate:
        logger.info(f"\n✗ Topics to DEACTIVATE ({len(to_deactivate)}):")
        for name in to_deactivate:
            logger.info(f"  ✗ {name} (will be set to inactive)")

    if not (to_add or to_update or to_deactivate):
        logger.info("\n✓ Database is in sync with YAML - no changes needed")

    logger.info("\n" + "=" * 80)


def sync_topics(
    config_loader: ConfigLoader,
    repository: Repository,
    dry_run: bool = False
) -> None:
    """
    Sync topics from YAML to database.

    Args:
        config_loader: Configuration loader instance
        repository: Database repository instance
        dry_run: If True, only show what would be done without making changes
    """
    logger.info("=" * 80)
    logger.info("SYNCING TOPICS FROM YAML TO DATABASE")
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    logger.info("=" * 80)

    yaml_topics = get_yaml_topics(config_loader)
    db_topics = repository.get_all_topics(active_only=False)
    db_topic_map = {topic.name: topic for topic in db_topics}

    to_add, to_update, to_deactivate = compare_topics(yaml_topics, db_topics)

    changes_made = 0

    # Add new topics
    if to_add:
        logger.info(f"\nAdding {len(to_add)} new topics:")
        for name in to_add:
            # Find the topic in YAML
            yaml_topic = None
            for topic_id, topic in yaml_topics.items():
                if topic.name == name:
                    yaml_topic = topic
                    break

            if yaml_topic:
                logger.info(f"  + {name}")
                if not dry_run:
                    repository.create_topic(
                        name=yaml_topic.name,
                        type=yaml_topic.type,
                        config=vars(yaml_topic),
                        is_active=True
                    )
                    changes_made += 1

    # Update existing topics
    if to_update:
        logger.info(f"\nUpdating {len(to_update)} existing topics:")
        for name in to_update:
            # Find the topic in YAML
            yaml_topic = None
            for topic_id, topic in yaml_topics.items():
                if topic.name == name:
                    yaml_topic = topic
                    break

            if yaml_topic:
                db_topic = db_topic_map[name]
                logger.info(f"  ↻ {name} (ID: {db_topic.id})")

                # Show what's changing
                old_config = db_topic.config
                new_config = vars(yaml_topic)

                changed_fields = []
                for key in new_config:
                    if key not in old_config or old_config[key] != new_config[key]:
                        changed_fields.append(key)

                if changed_fields:
                    logger.info(f"    Changed fields: {', '.join(changed_fields)}")

                if not dry_run:
                    repository.update_topic(
                        topic_id=db_topic.id,
                        config=new_config,
                        is_active=True  # Reactivate if it was inactive
                    )
                    changes_made += 1

    # Deactivate removed topics
    if to_deactivate:
        logger.info(f"\nDeactivating {len(to_deactivate)} removed topics:")
        for name in to_deactivate:
            db_topic = db_topic_map[name]
            if db_topic.is_active:
                logger.info(f"  ✗ {name} (ID: {db_topic.id}) - setting to inactive")
                if not dry_run:
                    repository.update_topic(
                        topic_id=db_topic.id,
                        config=db_topic.config,
                        is_active=False
                    )
                    changes_made += 1
            else:
                logger.info(f"  - {name} (ID: {db_topic.id}) - already inactive")

    logger.info("\n" + "=" * 80)
    if dry_run:
        logger.info(f"DRY RUN complete - {len(to_add) + len(to_update) + len(to_deactivate)} changes would be made")
        logger.info("Run without --dry-run to apply changes")
    else:
        logger.info(f"Sync complete - {changes_made} changes made")
    logger.info("=" * 80)


def delete_topic(repository: Repository, topic_id: int) -> None:
    """Soft delete a topic (set is_active=False)."""
    logger.info("=" * 80)
    logger.info(f"DEACTIVATING TOPIC ID: {topic_id}")
    logger.info("=" * 80)

    topic = repository.get_topic(topic_id)

    if not topic:
        logger.error(f"Topic ID {topic_id} not found!")
        return

    if not topic.is_active:
        logger.info(f"Topic '{topic.name}' is already inactive")
        return

    # Show topic info
    logger.info(f"\nTopic to deactivate:")
    logger.info(f"  Name: {topic.name}")
    logger.info(f"  Type: {topic.type}")

    questions = repository.get_questions_for_topic(topic_id)
    logger.info(f"  Questions: {len(questions)}")

    # Confirm
    logger.info(f"\nNote: This will set is_active=False. The topic and its questions will be preserved.")
    logger.info(f"      You can reactivate it later with: python scripts/manage_topics.py activate {topic_id}")

    # Deactivate
    repository.update_topic(
        topic_id=topic_id,
        config=topic.config,
        is_active=False
    )

    logger.info(f"\n✓ Topic '{topic.name}' has been deactivated")
    logger.info("=" * 80)


def activate_topic(repository: Repository, topic_id: int) -> None:
    """Reactivate a deactivated topic."""
    logger.info("=" * 80)
    logger.info(f"ACTIVATING TOPIC ID: {topic_id}")
    logger.info("=" * 80)

    topic = repository.get_topic(topic_id)

    if not topic:
        logger.error(f"Topic ID {topic_id} not found!")
        return

    if topic.is_active:
        logger.info(f"Topic '{topic.name}' is already active")
        return

    # Show topic info
    logger.info(f"\nTopic to activate:")
    logger.info(f"  Name: {topic.name}")
    logger.info(f"  Type: {topic.type}")

    questions = repository.get_questions_for_topic(topic_id)
    logger.info(f"  Questions: {len(questions)}")

    # Activate
    repository.update_topic(
        topic_id=topic_id,
        config=topic.config,
        is_active=True
    )

    logger.info(f"\n✓ Topic '{topic.name}' has been activated")
    logger.info("=" * 80)


def export_topics(repository: Repository, output_file: str = None) -> None:
    """Export current database topics to YAML format."""
    logger.info("=" * 80)
    logger.info("EXPORTING TOPICS TO YAML")
    logger.info("=" * 80)

    topics = repository.get_all_topics(active_only=False)

    if not topics:
        logger.error("No topics found in database!")
        return

    # Build YAML content
    yaml_lines = ["# Topics exported from database", f"# Export date: {datetime.utcnow()}", "", "topics:"]

    for topic in topics:
        # Create topic ID from name (lowercase, replace spaces with underscores)
        topic_id = topic.name.lower().replace(' ', '_').replace('-', '_')

        yaml_lines.append(f"  {topic_id}:")
        yaml_lines.append(f"    name: \"{topic.name}\"")
        yaml_lines.append(f"    type: {topic.type}")

        # Export config fields
        config = topic.config
        for key, value in sorted(config.items()):
            if isinstance(value, str):
                yaml_lines.append(f"    {key}: \"{value}\"")
            elif isinstance(value, (int, float, bool)):
                yaml_lines.append(f"    {key}: {value}")
            elif isinstance(value, dict):
                yaml_lines.append(f"    {key}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        yaml_lines.append(f"      {sub_key}: \"{sub_value}\"")
                    else:
                        yaml_lines.append(f"      {sub_key}: {sub_value}")

        # Note if inactive
        if not topic.is_active:
            yaml_lines.append(f"    # NOTE: This topic is currently INACTIVE in database")

        yaml_lines.append("")

    yaml_content = "\n".join(yaml_lines)

    # Determine output file
    if not output_file:
        output_file = f"topics_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.yaml"

    # Write to file
    output_path = Path(output_file)
    output_path.write_text(yaml_content, encoding='utf-8')

    logger.info(f"\n✓ Exported {len(topics)} topics to: {output_file}")
    logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Manage learning topics for Telegram Learning Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  list                    List all topics with their current parameters
  sync                    Sync topics from YAML to database
  delete <topic_id>       Deactivate a topic (soft delete)
  activate <topic_id>     Reactivate a deactivated topic
  export                  Export current database topics to YAML
  diff                    Show differences between YAML and database

Examples:
  python scripts/manage_topics.py list
  python scripts/manage_topics.py sync --dry-run
  python scripts/manage_topics.py sync
  python scripts/manage_topics.py delete 3
  python scripts/manage_topics.py activate 3
  python scripts/manage_topics.py export --output backup.yaml
  python scripts/manage_topics.py diff
        """
    )

    parser.add_argument(
        'command',
        choices=['list', 'sync', 'delete', 'activate', 'export', 'diff'],
        help='Command to execute'
    )

    parser.add_argument(
        'topic_id',
        type=int,
        nargs='?',
        help='Topic ID (required for delete/activate commands)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes (sync only)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (export only)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.command in ['delete', 'activate'] and not args.topic_id:
        logger.error(f"Topic ID is required for '{args.command}' command")
        parser.print_help()
        sys.exit(1)

    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./learning_bot.db')
    repository = Repository(db_url)

    # Initialize config loader for commands that need it
    config_loader = None
    if args.command in ['sync', 'diff']:
        config_dir = os.getenv('CONFIG_DIR', 'config')
        config_loader = ConfigLoader(config_dir)

    try:
        # Execute command
        if args.command == 'list':
            list_topics(repository)

        elif args.command == 'sync':
            sync_topics(config_loader, repository, dry_run=args.dry_run)

        elif args.command == 'delete':
            delete_topic(repository, args.topic_id)

        elif args.command == 'activate':
            activate_topic(repository, args.topic_id)

        elif args.command == 'export':
            export_topics(repository, output_file=args.output)

        elif args.command == 'diff':
            show_diff(config_loader, repository)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
