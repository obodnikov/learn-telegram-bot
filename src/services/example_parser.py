"""Example parser service for loading and managing example question files."""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import random
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "question_text": self.question,
            "choice_a": self.choices.get("A", ""),
            "choice_b": self.choices.get("B", ""),
            "choice_c": self.choices.get("C", ""),
            "choice_d": self.choices.get("D", ""),
            "correct_answer": self.correct,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "tags": self.tags
        }


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
        logger.info(f"Loading examples from: {file_path}")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Example file not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "questions" not in data:
                raise ExampleFileError("Missing 'questions' key in example file")

            if not isinstance(data["questions"], list):
                raise ExampleFileError("'questions' must be a list")

            examples = []
            for i, q_data in enumerate(data["questions"]):
                try:
                    example = self._parse_question(q_data)
                    examples.append(example)
                except Exception as e:
                    logger.warning(f"Failed to parse question {i} in {file_path}: {e}")
                    continue

            if not examples:
                raise ExampleFileError(f"No valid questions found in {file_path}")

            logger.info(f"Loaded {len(examples)} example questions from {file_path}")
            return examples

        except json.JSONDecodeError as e:
            raise ExampleFileError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ExampleFileError)):
                raise
            raise ExampleFileError(f"Error loading examples from {file_path}: {e}")

    def _parse_question(self, q_data: Dict[str, Any]) -> ExampleQuestion:
        """
        Parse a single question from JSON data.

        Args:
            q_data: Question data dictionary

        Returns:
            ExampleQuestion object

        Raises:
            ExampleFileError: If question data is invalid
        """
        required_fields = ["question", "choices", "correct", "explanation", "difficulty"]
        missing = [f for f in required_fields if f not in q_data]
        if missing:
            raise ExampleFileError(f"Missing required fields: {missing}")

        # Validate choices
        choices = q_data["choices"]
        if not isinstance(choices, dict):
            raise ExampleFileError("'choices' must be a dictionary")

        required_choices = ["A", "B", "C", "D"]
        missing_choices = [c for c in required_choices if c not in choices]
        if missing_choices:
            raise ExampleFileError(f"Missing choices: {missing_choices}")

        # Validate correct answer
        correct = q_data["correct"].upper()
        if correct not in required_choices:
            raise ExampleFileError(f"Invalid correct answer: {correct}")

        return ExampleQuestion(
            question=q_data["question"],
            choices=choices,
            correct=correct,
            explanation=q_data["explanation"],
            difficulty=q_data["difficulty"].lower(),
            tags=q_data.get("tags", [])
        )

    def filter_unused_examples(
        self,
        examples: List[ExampleQuestion],
        existing_questions: List[Any]
    ) -> List[ExampleQuestion]:
        """
        Filter out examples that already exist in the database.

        Args:
            examples: All example questions
            existing_questions: Existing questions from database

        Returns:
            List of unused example questions
        """
        if not existing_questions:
            return examples

        # Build set of existing question texts for fast lookup
        existing_texts = {q.question_text.strip().lower() for q in existing_questions}

        # Filter out examples that already exist
        unused = [
            ex for ex in examples
            if ex.question.strip().lower() not in existing_texts
        ]

        logger.info(
            f"Filtered examples: {len(examples)} total, "
            f"{len(unused)} unused, {len(examples) - len(unused)} already in database"
        )

        return unused

    def select_questions_for_hybrid(
        self,
        examples: List[ExampleQuestion],
        total_needed: int,
        use_ratio: float
    ) -> Tuple[List[ExampleQuestion], int]:
        """
        For hybrid mode: select questions from examples and calculate how many to generate.

        Args:
            examples: All available example questions (should be pre-filtered to unused only)
            total_needed: Total questions needed
            use_ratio: Ratio of provided vs generated (0.3 = 30% from file)

        Returns:
            Tuple of (selected_examples, num_to_generate)
        """
        if not examples:
            logger.info("Hybrid mode: no unused examples available, will generate all questions")
            return [], total_needed

        # Calculate how many to use from examples
        num_from_file = int(total_needed * use_ratio)
        num_from_file = max(0, min(num_from_file, len(examples)))  # Between 0 and available

        # Calculate how many to generate
        num_to_generate = total_needed - num_from_file

        # Randomly select from examples
        if num_from_file > 0:
            selected = random.sample(examples, num_from_file)
        else:
            selected = []

        logger.info(
            f"Hybrid mode: selected {num_from_file} from file, "
            f"will generate {num_to_generate} new questions"
        )

        return selected, num_to_generate

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
        if not examples:
            return ""

        formatted_parts = []

        if mode == "augment":
            # For augment mode: show full examples for the LLM to learn from
            formatted_parts.append("Here are example questions to guide your generation:\n")
            for i, example in enumerate(examples, 1):
                formatted_parts.append(f"\nExample {i}:")
                formatted_parts.append(json.dumps(example.to_dict(), indent=2, ensure_ascii=False))

        elif mode == "template":
            # For template mode: show structure/pattern to follow
            formatted_parts.append("Follow this exact structure for each question:\n")
            if examples:
                # Show one example as template
                formatted_parts.append(json.dumps(examples[0].to_dict(), indent=2, ensure_ascii=False))

        elif mode == "hybrid":
            # For hybrid mode: show examples as reference
            formatted_parts.append("Here are some example questions for reference:\n")
            # Show up to 3 examples
            for i, example in enumerate(examples[:3], 1):
                formatted_parts.append(f"\nExample {i}:")
                formatted_parts.append(json.dumps(example.to_dict(), indent=2, ensure_ascii=False))

        return "\n".join(formatted_parts)

    def convert_to_db_format(
        self,
        examples: List[ExampleQuestion],
        topic_id: int,
        source: str = "file",
        source_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert example questions to database-ready format.

        Args:
            examples: List of example questions
            topic_id: Topic ID for the questions
            source: Question source ('file', 'llm', 'hybrid')
            source_file: Path to source file

        Returns:
            List of dictionaries ready for database insertion
        """
        db_questions = []

        for example in examples:
            question_data = {
                "topic_id": topic_id,
                "question_text": example.question,
                "choice_a": example.choices["A"],
                "choice_b": example.choices["B"],
                "choice_c": example.choices["C"],
                "choice_d": example.choices["D"],
                "correct_answer": example.correct,
                "explanation": example.explanation,
                "difficulty": example.difficulty,
                "tags": example.tags,
                "source": source,
                "source_file": source_file,
                "quality_score": 0.5  # Default quality score
            }
            db_questions.append(question_data)

        logger.info(f"Converted {len(db_questions)} examples to database format")
        return db_questions
