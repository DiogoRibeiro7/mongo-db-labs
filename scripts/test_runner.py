#!/usr/bin/env python3
"""
Local test runner for MongoDB Labs.
Provides quick testing during development.

Usage:
    python scripts/test_runner.py              # Run all fast tests
    python scripts/test_runner.py --slow       # Include slow tests
    python scripts/test_runner.py --lab iot    # Test specific lab
    python scripts/test_runner.py --coverage   # Generate coverage report
"""

import sys
import subprocess
import argparse
from pathlib import Path
import os


def check_mongodb():
    """Check if MongoDB is available."""
    try:
        from pymongo import MongoClient
        client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
                            serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        print(f"⚠️  MongoDB not available: {e}")
        return False


def run_tests(args):
    """Run pytest with appropriate arguments."""
    cmd = [sys.executable, "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # Test selection
    if args.lab:
        cmd.extend(["-k", args.lab])

    if args.slow:
        # Include all tests
        cmd.append("tests/")
    else:
        # Exclude slow tests
        cmd.extend(["-m", "not slow", "tests/"])

    # Coverage
    if args.coverage:
        cmd.extend([
            "--cov=labs",
            "--cov=scripts",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])

    # Specific test file
    if args.test:
        cmd.append(f"tests/{args.test}")

    # Show test output
    if args.capture == "no":
        cmd.append("-s")

    # Add color
    cmd.append("--color=yes")

    # Run tests
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for MongoDB Labs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_runner.py                    # Quick tests only
  python scripts/test_runner.py --slow             # All tests
  python scripts/test_runner.py --lab iot_flood    # Test specific lab
  python scripts/test_runner.py --coverage         # With coverage report
  python scripts/test_runner.py -t test_setup      # Run specific test file
        """
    )

    parser.add_argument("--slow", action="store_true",
                       help="Include slow tests (simulations)")
    parser.add_argument("--lab", help="Test specific lab (pattern matching)")
    parser.add_argument("-t", "--test", help="Run specific test file")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--capture", choices=["yes", "no"], default="yes",
                       help="Capture stdout/stderr")
    parser.add_argument("--no-mongo-check", action="store_true",
                       help="Skip MongoDB availability check")

    args = parser.parse_args()

    # Check environment
    print("=" * 60)
    print("MongoDB Labs Test Runner")
    print("=" * 60)

    # Check MongoDB
    if not args.no_mongo_check:
        print("Checking MongoDB connection...")
        if not check_mongodb():
            print("\n❌ MongoDB is required for tests")
            print("Start MongoDB with: docker-compose up -d")
            return 1
        print("✅ MongoDB is available")

    # Check pytest
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not installed")
        print("Install with: pip install -r requirements-test.txt")
        return 1

    print("-" * 60)

    # Run tests
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())