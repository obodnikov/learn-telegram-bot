#!/usr/bin/env python3
"""Export best performing questions to a file."""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)


def main():
    """Export high-quality questions."""
    parser = argparse.ArgumentParser(
        description="Export best performing questions to example file"
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic ID to export"
    )
    parser.add_argument(
        "--min-quality",
        type=float,
        default=0.8,
        help="Minimum quality score (default: 0.8)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: config/examples/{topic}_best.json)"
    )
    parser.add_argument(
        "--min-attempts",
        type=int,
        default=10,
        help="Minimum number of attempts (default: 10)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Export Best Questions")
    logger.info("=" * 60)
    logger.info(f"Topic: {args.topic}")
    logger.info(f"Min Quality: {args.min_quality}")
    logger.info(f"Min Attempts: {args.min_attempts}")
    
    # TODO: Phase 5 - Implement actual export
    logger.warning("This script will be implemented in Phase 5")
    logger.info("\nPlanned functionality:")
    logger.info("1. Query database for questions with quality >= min-quality")
    logger.info("2. Filter by minimum attempts")
    logger.info("3. Sort by quality score")
    logger.info("4. Export to JSON file in example format")
    logger.info("5. Include metadata about source (LLM-generated)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
