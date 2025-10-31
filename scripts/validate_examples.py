#!/usr/bin/env python3
"""Manually validate all example files."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.validator import ExampleValidator
from src.utils.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)


def main():
    """Run validation on all example files."""
    logger.info("=" * 60)
    logger.info("Manual Example File Validation")
    logger.info("=" * 60)
    
    validator = ExampleValidator()
    examples_dir = project_root / "config" / "examples"
    
    if not examples_dir.exists():
        logger.error(f"Examples directory not found: {examples_dir}")
        return 1
    
    summary = validator.validate_all_examples(str(examples_dir))
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files: {summary['total']}")
    logger.info(f"Valid: {summary['valid']}")
    logger.info(f"Invalid: {summary['invalid']}")
    
    if summary['invalid'] > 0:
        logger.info("\n❌ INVALID FILES:")
        for file_result in summary['files']:
            if not file_result['is_valid']:
                logger.info(f"\n  File: {file_result['file_path']}")
                for error in file_result['errors']:
                    logger.info(f"    - {error}")
        return 1
    else:
        logger.info("\n✅ All files valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
