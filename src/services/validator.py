"""Validate example question files."""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from jsonschema import validate, ValidationError as JsonSchemaError
from src.utils.exceptions import ExampleFileError, ValidationError
from src.utils.logger import get_logger
from src.utils.difficulty import DifficultyManager

logger = get_logger(__name__)


class ExampleValidator:
    """Validate example question files against schema."""
    
    # JSON Schema for example files
    EXAMPLE_SCHEMA = {
        "type": "object",
        "required": ["meta", "questions"],
        "properties": {
            "meta": {
                "type": "object",
                "required": ["topic", "difficulty", "total_questions"],
                "properties": {
                    "topic": {"type": "string"},
                    "target_language": {"type": "string"},
                    "native_language": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "total_questions": {"type": "integer", "minimum": 1},
                    "created_by": {"type": "string"},
                    "notes": {"type": "string"}
                }
            },
            "questions": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["question", "choices", "correct", "explanation"],
                    "properties": {
                        "question": {"type": "string", "minLength": 10},
                        "choices": {
                            "type": "object",
                            "required": ["A", "B", "C", "D"],
                            "properties": {
                                "A": {"type": "string", "minLength": 1},
                                "B": {"type": "string", "minLength": 1},
                                "C": {"type": "string", "minLength": 1},
                                "D": {"type": "string", "minLength": 1}
                            }
                        },
                        "correct": {
                            "type": "string",
                            "pattern": "^[ABCD]$"
                        },
                        "explanation": {"type": "string", "minLength": 20},
                        "difficulty": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
    
    def __init__(self):
        """Initialize validator."""
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a single example file.
        
        Args:
            file_path: Path to example JSON file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return False, errors
        
        # Load JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors
        
        # Validate against schema
        try:
            validate(instance=data, schema=self.EXAMPLE_SCHEMA)
        except JsonSchemaError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, errors
        
        # Additional semantic validation
        semantic_errors = self._validate_semantics(data)
        errors.extend(semantic_errors)
        
        is_valid = len(errors) == 0
        
        # Log result
        self.validation_results.append({
            'file_path': str(file_path),
            'is_valid': is_valid,
            'errors': errors,
            'question_count': len(data.get('questions', []))
        })
        
        if is_valid:
            logger.info(f"✓ Valid: {file_path.name} ({len(data['questions'])} questions)")
        else:
            logger.error(f"✗ Invalid: {file_path.name} - {len(errors)} errors")
            for error in errors:
                logger.error(f"  - {error}")
        
        return is_valid, errors
    
    def _validate_semantics(self, data: Dict[str, Any]) -> List[str]:
        """
        Perform semantic validation beyond schema.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            List of semantic errors
        """
        errors = []
        meta = data.get('meta', {})
        questions = data.get('questions', [])
        
        # Validate difficulty level
        difficulty = meta.get('difficulty', '')
        if not DifficultyManager.validate_difficulty(difficulty):
            errors.append(
                f"Invalid difficulty '{difficulty}'. Must be one of: {DifficultyManager.VALID_LEVELS}"
            )
        
        # Validate question count matches meta
        declared_count = meta.get('total_questions', 0)
        actual_count = len(questions)
        if declared_count != actual_count:
            errors.append(
                f"Meta declares {declared_count} questions but file contains {actual_count}"
            )
        
        # Validate each question
        for idx, question in enumerate(questions, 1):
            # Check all choices are unique
            choices = question.get('choices', {})
            choice_values = list(choices.values())
            if len(choice_values) != len(set(choice_values)):
                errors.append(f"Question {idx}: Duplicate choices found")
            
            # Check correct answer exists in choices
            correct = question.get('correct', '')
            if correct not in choices:
                errors.append(f"Question {idx}: Correct answer '{correct}' not in choices")
            
            # Check explanation has minimum content
            explanation = question.get('explanation', '')
            if len(explanation) < 50:
                errors.append(f"Question {idx}: Explanation too short (minimum 50 chars)")
            
            # For language questions, check bilingual explanations
            if 'target_language' in meta and 'native_language' in meta:
                target_lang = meta['target_language']
                native_lang = meta['native_language']
                if native_lang not in explanation:
                    errors.append(
                        f"Question {idx}: Explanation missing native language ({native_lang})"
                    )
                if target_lang not in explanation:
                    errors.append(
                        f"Question {idx}: Explanation missing target language ({target_lang})"
                    )
        
        return errors
    
    def validate_all_examples(self, examples_dir: str) -> Dict[str, Any]:
        """
        Validate all example files in directory.
        
        Args:
            examples_dir: Directory containing example files
            
        Returns:
            Summary of validation results
        """
        examples_path = Path(examples_dir)
        
        if not examples_path.exists():
            logger.warning(f"Examples directory not found: {examples_dir}")
            return {'total': 0, 'valid': 0, 'invalid': 0, 'files': []}
        
        json_files = list(examples_path.glob("*.json"))
        logger.info(f"Validating {len(json_files)} example files...")
        
        self.validation_results = []
        
        for json_file in json_files:
            self.validate_file(str(json_file))
        
        valid_count = sum(1 for r in self.validation_results if r['is_valid'])
        invalid_count = len(self.validation_results) - valid_count
        
        summary = {
            'total': len(self.validation_results),
            'valid': valid_count,
            'invalid': invalid_count,
            'files': self.validation_results
        }
        
        logger.info(f"Validation complete: {valid_count}/{len(self.validation_results)} files valid")
        
        if invalid_count > 0:
            logger.warning(f"{invalid_count} files have validation errors!")
        
        return summary
