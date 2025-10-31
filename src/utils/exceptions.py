"""Custom exceptions for the learning bot."""


class BotError(Exception):
    """Base exception for all bot errors."""
    pass


class ConfigurationError(BotError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(BotError):
    """Raised when validation fails."""
    pass


class ExampleFileError(ValidationError):
    """Raised when example file is invalid."""
    
    def __init__(self, file_path: str, errors: list[str]):
        """
        Initialize ExampleFileError.
        
        Args:
            file_path: Path to the invalid file
            errors: List of validation errors
        """
        self.file_path = file_path
        self.errors = errors
        super().__init__(f"Invalid example file {file_path}: {', '.join(errors)}")


class LLMServiceError(BotError):
    """Raised when LLM service fails."""
    pass


class DatabaseError(BotError):
    """Raised when database operation fails."""
    pass


class QuestionGenerationError(BotError):
    """Raised when question generation fails."""
    pass
