"""Load and validate configuration files."""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.utils.exceptions import ConfigurationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TopicConfig:
    """Configuration for a single topic."""
    
    name: str
    type: str
    difficulty: str
    questions_per_batch: int
    context: str
    target_language: Optional[str] = None
    native_language: Optional[str] = None
    time_period: Optional[str] = None
    examples: Optional[Dict[str, Any]] = None


class ConfigLoader:
    """Load and manage configuration files."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
            
        Raises:
            ConfigurationError: If config directory not found
        """
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise ConfigurationError(f"Config directory not found: {config_dir}")
        
        self.topics: Dict[str, TopicConfig] = {}
        self.prompts: Dict[str, Any] = {}
        self.difficulty_levels: Dict[str, Any] = {}
        
        logger.info(f"ConfigLoader initialized with directory: {config_dir}")
    
    def load_all(self) -> None:
        """Load all configuration files."""
        logger.info("Loading all configuration files...")
        self.load_topics()
        self.load_prompts()
        self.load_difficulty_levels()
        logger.info("All configurations loaded successfully")
    
    def load_topics(self) -> Dict[str, TopicConfig]:
        """
        Load topics configuration.
        
        Returns:
            Dictionary of topic configurations
            
        Raises:
            ConfigurationError: If topics.yaml is invalid
        """
        topics_file = self.config_dir / "topics.yaml"
        
        if not topics_file.exists():
            raise ConfigurationError(f"Topics file not found: {topics_file}")
        
        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if 'topics' not in data:
                raise ConfigurationError("'topics' key not found in topics.yaml")
            
            for topic_id, topic_data in data['topics'].items():
                self.topics[topic_id] = TopicConfig(
                    name=topic_data['name'],
                    type=topic_data['type'],
                    difficulty=topic_data['difficulty'],
                    questions_per_batch=topic_data['questions_per_batch'],
                    context=topic_data['context'],
                    target_language=topic_data.get('target_language'),
                    native_language=topic_data.get('native_language'),
                    time_period=topic_data.get('time_period'),
                    examples=topic_data.get('examples')
                )
            
            logger.info(f"Loaded {len(self.topics)} topics")
            return self.topics
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in topics.yaml: {e}")
        except KeyError as e:
            raise ConfigurationError(f"Missing required field in topics.yaml: {e}")
    
    def load_prompts(self) -> Dict[str, Any]:
        """
        Load prompt templates.
        
        Returns:
            Dictionary of prompt templates
        """
        prompts_file = self.config_dir / "prompts.yaml"
        
        if not prompts_file.exists():
            logger.warning(f"Prompts file not found: {prompts_file}")
            return {}
        
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            
            logger.info("Prompts loaded successfully")
            return self.prompts
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in prompts.yaml: {e}")
    
    def load_difficulty_levels(self) -> Dict[str, Any]:
        """
        Load difficulty level definitions.
        
        Returns:
            Dictionary of difficulty levels
        """
        difficulty_file = self.config_dir / "difficulty_levels.yaml"
        
        if not difficulty_file.exists():
            logger.warning(f"Difficulty levels file not found: {difficulty_file}")
            return {}
        
        try:
            with open(difficulty_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.difficulty_levels = data.get('difficulty_levels', {})
            logger.info(f"Loaded {len(self.difficulty_levels)} difficulty levels")
            return self.difficulty_levels
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in difficulty_levels.yaml: {e}")
    
    def get_topic(self, topic_id: str) -> TopicConfig:
        """
        Get configuration for a specific topic.
        
        Args:
            topic_id: Topic identifier
            
        Returns:
            Topic configuration
            
        Raises:
            ConfigurationError: If topic not found
        """
        if topic_id not in self.topics:
            raise ConfigurationError(f"Topic not found: {topic_id}")
        return self.topics[topic_id]
    
    def get_prompt(self, topic_type: str, mode: str) -> str:
        """
        Get prompt template for topic type and mode.
        
        Args:
            topic_type: Type of topic (language, history, etc.)
            mode: Generation mode (augment, template, hybrid, standard)
            
        Returns:
            Prompt template string
        """
        try:
            return self.prompts['question_generation'][topic_type][f'{mode}_prompt']
        except KeyError:
            logger.warning(f"Prompt not found for {topic_type}/{mode}, using default")
            return self.prompts.get('question_generation', {}).get('default', {}).get('standard_prompt', '')
