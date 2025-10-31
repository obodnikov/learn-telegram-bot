#!/usr/bin/env python3
"""Run all tests for the project."""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


def run_tests():
    """Run pytest with coverage."""
    print("=" * 60)
    print("Running Tests")
    print("=" * 60)
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def run_validation():
    """Run startup validation."""
    print("\n" + "=" * 60)
    print("Running Startup Validation")
    print("=" * 60)
    
    cmd = ["python", "scripts/validate_examples.py"]
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def main():
    """Run all checks."""
    print("Running all project checks...")
    
    # Run tests
    test_result = run_tests()
    
    # Run validation
    validation_result = run_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests: {'✅ PASSED' if test_result == 0 else '❌ FAILED'}")
    print(f"Validation: {'✅ PASSED' if validation_result == 0 else '❌ FAILED'}")
    print("=" * 60)
    
    return max(test_result, validation_result)


if __name__ == "__main__":
    sys.exit(main())
