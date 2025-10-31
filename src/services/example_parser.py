"""Example parser service - placeholder for Phase 2."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass
from src.utils.logger import get_logger
from src.utils.exceptions import ExampleFileError

logger = get_logger(__name__)


@dataclass
class ExampleQuestion:
    """Represents a single example question."""
    question: str
    choices: Dict[str, str]
    correct: str
    explanation: str
    difficulty: str
    tags: List[str]


@dataclass
class ExampleConfig:
    """Configuration for example questions."""
    file: str
    mode: str  # augment, template, hybrid
    use_ratio: float = 0.5


class ExampleParser:
    """Parse and manage example question files."""
    
    def __init__(self):
        """Initialize example parser."""
        logger.info("ExampleParser initialized")
    
    def load_examples(self, file_path: str) -> List[ExampleQuestion]:
        """
        Load example questions from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of ExampleQuestion objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ExampleFileError: If JSON is invalid
        """
        # TODO: Phase 2 - Implement
        logger.info(f"Loading examples from: {file_path}")
        pass
    
    def select_questions_for_hybrid(
        self, 
        examples: List[ExampleQuestion], 
        total_needed: int, 
        use_ratio: float
    ) -> tuple[List[ExampleQuestion], int]:
        """
        For hybrid mode: select questions from examples and calculate how many to generate.
        
        Args:
            examples: All available example questions
            total_needed: Total questions needed
            use_ratio: Ratio of provided vs generated (0.3 = 30% from file)
            
        Returns:
            Tuple of (selected_examples, num_to_generate)
        """
        # TODO: Phase 2 - Implement
        pass
    
    def format_examples_for_prompt(
        self, 
        examples: List[ExampleQuestion],
        mode: str
    ) -> str:
        """
        Format examples for inclusion in LLM prompt.
        
        Args:
            examples: Example questions
            mode: Generation mode (augment/template/hybrid)
            
        Returns:
            Formatted string for prompt
        """
        # TODO: Phase 2 - Implement
        pass
