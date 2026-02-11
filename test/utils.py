#!/usr/bin/env python3
"""Utility functions for testing."""


def greet(name: str) -> str:
    """Generate a greeting message."""
    return f"Hello, {name}!"


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def calculate_stats(numbers: list) -> dict:
    """Calculate basic statistics."""
    if not numbers:
        return {"count": 0, "sum": 0, "avg": 0}

    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "avg": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }
