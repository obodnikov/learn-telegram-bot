"""Tests for example file validator."""
import pytest
import json
from pathlib import Path
from src.services.validator import ExampleValidator


def test_validator_initialization():
    """Test that validator initializes correctly."""
    validator = ExampleValidator()
    assert validator is not None
    assert validator.validation_results == []


def test_validate_missing_file():
    """Test validation of non-existent file."""
    validator = ExampleValidator()
    is_valid, errors = validator.validate_file("nonexistent.json")
    
    assert is_valid is False
    assert len(errors) > 0
    assert "File not found" in errors[0]


def test_validate_invalid_json():
    """Test validation of invalid JSON."""
    validator = ExampleValidator()
    
    # Create temporary invalid JSON file
    temp_file = Path("/tmp/invalid.json")
    temp_file.write_text("{ invalid json }")
    
    is_valid, errors = validator.validate_file(str(temp_file))
    
    assert is_valid is False
    assert len(errors) > 0
    assert "Invalid JSON" in errors[0]
    
    # Cleanup
    temp_file.unlink()


def test_validate_schema():
    """Test schema validation."""
    validator = ExampleValidator()
    
    # Create temporary file with invalid schema
    temp_file = Path("/tmp/invalid_schema.json")
    data = {
        "meta": {"topic": "test"},  # Missing required fields
        "questions": []
    }
    temp_file.write_text(json.dumps(data))
    
    is_valid, errors = validator.validate_file(str(temp_file))
    
    assert is_valid is False
    assert len(errors) > 0
    
    # Cleanup
    temp_file.unlink()


# Add more tests as needed
