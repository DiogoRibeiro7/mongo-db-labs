#!/usr/bin/env python3
"""
Test Docker Setup for MongoDB Labs
Run this to verify Docker integration is working correctly.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ SUCCESS")
        if result.stdout:
            print(f"Output:\n{result.stdout[:500]}")
    else:
        print(f"✗ FAILED (exit code: {result.returncode})")
        if result.stderr:
            print(f"Error:\n{result.stderr[:500]}")

    return result.returncode == 0

def main():
    print("MongoDB Labs - Docker Integration Test")
    print("="*60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Check if docker-compose.yml exists
    compose_file = Path("docker-compose.yml")
    if compose_file.exists():
        print("✓ docker-compose.yml found")
        tests_passed += 1
    else:
        print("✗ docker-compose.yml not found")
        tests_failed += 1
        return 1

    # Test 2: Check wait_for_mongo.py exists
    wait_script = Path("scripts/wait_for_mongo.py")
    if wait_script.exists():
        print("✓ wait_for_mongo.py found")
        tests_passed += 1
    else:
        print("✗ wait_for_mongo.py not found")
        tests_failed += 1

    # Test 3: Check Docker is installed
    if run_command(["docker", "--version"], "Docker installation"):
        tests_passed += 1
    else:
        tests_failed += 1
        print("Docker not installed or not in PATH")

    # Test 4: Check Docker Compose
    if run_command(["docker-compose", "--version"], "Docker Compose installation"):
        tests_passed += 1
    else:
        # Try new syntax
        if run_command(["docker", "compose", "version"], "Docker Compose (new syntax)"):
            tests_passed += 1
        else:
            tests_failed += 1

    # Test 5: Check lab.py with --help
    if run_command(["python", "scripts/lab.py", "--help"], "Lab runner help"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 6: List labs
    if run_command(["python", "scripts/lab.py", "list"], "List available labs"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")

    if tests_failed == 0:
        print("\n✓ All tests passed! Docker integration is ready.")
        print("\nNext steps:")
        print("1. Start MongoDB: docker-compose up -d")
        print("2. Run a lab: python scripts/lab.py all iot_flood_demo --docker")
        return 0
    else:
        print(f"\n✗ {tests_failed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())