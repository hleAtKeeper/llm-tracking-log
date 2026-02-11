#!/usr/bin/env python3
"""Main test script to demonstrate dependency tracking."""

import sys
from pathlib import Path

# Import local modules (these should be captured as dependencies)
from utils import greet, add_numbers, calculate_stats
from config import APP_NAME, VERSION, DEBUG


def main():
    """Run the test application."""
    print(f"{APP_NAME} v{VERSION}")
    print(f"Debug mode: {DEBUG}")
    print("-" * 50)

    # Test greeting
    message = greet("World")
    print(message)

    # Test addition
    result = add_numbers(10, 20)
    print(f"10 + 20 = {result}")

    # Test statistics
    numbers = [1, 2, 3, 4, 5, 10, 15, 20]
    stats = calculate_stats(numbers)
    print(f"\nStatistics for {numbers}:")
    print(f"  Count: {stats['count']}")
    print(f"  Sum: {stats['sum']}")
    print(f"  Average: {stats['avg']:.2f}")
    print(f"  Min: {stats['min']}")
    print(f"  Max: {stats['max']}")


if __name__ == "__main__":
    main()
