"""Application startup and validation."""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger, get_logger
from src.services.validator import ExampleValidator
from src.utils.exceptions import ConfigurationError, ValidationError

logger = get_logger(__name__)


class StartupValidator:
    """Validate application configuration and files on startup."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize startup validator.
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self.config_loader = ConfigLoader(config_dir)
        self.example_validator = ExampleValidator()
    
    def run_startup_checks(self) -> bool:
        """
        Run all startup validation checks.
        
        Returns:
            True if all checks pass, False otherwise
            
        Raises:
            ConfigurationError: If critical configuration is invalid
        """
        logger.info("=" * 60)
        logger.info("Running startup validation checks...")
        logger.info("=" * 60)
        
        try:
            # 1. Load configurations
            logger.info("Step 1: Loading configurations...")
            self.config_loader.load_all()
            logger.info("✓ Configurations loaded successfully")
            
            # 2. Validate example files
            logger.info("\nStep 2: Validating example files...")
            examples_dir = Path(self.config_dir) / "examples"
            validation_summary = self.example_validator.validate_all_examples(str(examples_dir))
            
            if validation_summary['invalid'] > 0:
                logger.warning(
                    f"⚠ {validation_summary['invalid']} example files have validation errors"
                )
                # Don't fail startup, but warn
                for file_result in validation_summary['files']:
                    if not file_result['is_valid']:
                        logger.warning(f"  File: {file_result['file_path']}")
                        for error in file_result['errors']:
                            logger.warning(f"    - {error}")
            else:
                logger.info("✓ All example files valid")
            
            # 3. Validate topic-example references
            logger.info("\nStep 3: Validating topic-example references...")
            self._validate_topic_example_refs()
            logger.info("✓ Topic-example references valid")
            
            # 4. Check environment variables
            logger.info("\nStep 4: Checking environment variables...")
            self._check_env_variables()
            logger.info("✓ Environment variables configured")
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ All startup checks passed!")
            logger.info("=" * 60 + "\n")
            
            return True
            
        except ConfigurationError as e:
            logger.error(f"✗ Configuration error: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error during startup: {e}")
            raise
    
    def _validate_topic_example_refs(self) -> None:
        """Validate that topics reference existing example files."""
        for topic_id, topic in self.config_loader.topics.items():
            if topic.examples:
                example_file = topic.examples.get('file')
                if example_file:
                    file_path = Path(example_file)
                    if not file_path.exists():
                        logger.warning(
                            f"Topic '{topic_id}' references missing example file: {example_file}"
                        )
    
    def _check_env_variables(self) -> None:
        """Check required environment variables."""
        load_dotenv()
        
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENROUTER_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
