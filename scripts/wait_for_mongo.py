#!/usr/bin/env python3
"""
Wait for MongoDB to be ready before proceeding.
Supports both Docker and local MongoDB instances.
"""

import sys
import time
import subprocess
import argparse
from pathlib import Path

def check_mongo_ready(host="localhost", port=27017, auth=False, max_attempts=30):
    """
    Check if MongoDB is ready to accept connections.

    Args:
        host: MongoDB host (default: localhost)
        port: MongoDB port (default: 27017)
        auth: Whether authentication is required
        max_attempts: Maximum number of attempts (default: 30)

    Returns:
        True if MongoDB is ready, False otherwise
    """
    connection_string = f"mongodb://{host}:{port}/"

    if auth:
        # Use authenticated connection for Docker setup
        connection_string = f"mongodb://admin:adminpassword@{host}:{port}/admin?authSource=admin"

    # Build the mongosh command
    test_command = [
        "mongosh",
        connection_string,
        "--quiet",
        "--eval",
        "db.adminCommand('ping')"
    ]

    print(f"Waiting for MongoDB at {host}:{port}...")

    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(f"[OK] MongoDB is ready after {attempt + 1} attempts")
                return True

        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            print("[ERROR] mongosh not found. Please ensure MongoDB Shell is installed.")
            print("       Install from: https://www.mongodb.com/try/download/shell")
            return False
        except Exception as e:
            # MongoDB not ready yet, continue waiting
            pass

        # Show progress
        if (attempt + 1) % 5 == 0:
            print(f"  Still waiting... ({attempt + 1}/{max_attempts})")

        time.sleep(1)

    print(f"[ERROR] MongoDB did not become ready after {max_attempts} attempts")
    return False

def check_docker_running():
    """Check if Docker MongoDB container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=mongodb-labs", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            if "healthy" in result.stdout.lower():
                return "healthy"
            elif "up" in result.stdout.lower():
                return "running"
        return "not_running"

    except FileNotFoundError:
        print("[WARNING] Docker not found. Checking for local MongoDB...")
        return "docker_not_available"
    except Exception:
        return "not_running"

def check_local_mongo():
    """Check if local MongoDB service is running."""
    # Windows check
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["sc", "query", "MongoDB"],
                capture_output=True,
                text=True,
                shell=True
            )
            if "RUNNING" in result.stdout:
                return True
        except:
            pass

    # Unix-like systems
    else:
        try:
            result = subprocess.run(
                ["pgrep", "-x", "mongod"],
                capture_output=True
            )
            if result.returncode == 0:
                return True
        except:
            pass

    # Try to connect directly
    return check_mongo_ready(auth=False, max_attempts=1)

def start_docker_mongo():
    """Start Docker MongoDB if not running."""
    print("Starting MongoDB Docker container...")

    compose_file = Path(__file__).parent.parent / "docker-compose.yml"

    if not compose_file.exists():
        print(f"[ERROR] docker-compose.yml not found at {compose_file}")
        return False

    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "up", "-d", "mongodb"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Try with docker compose (newer syntax)
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "up", "-d", "mongodb"],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:
            print("[OK] Docker MongoDB starting...")
            return True
        else:
            print(f"[ERROR] Failed to start Docker: {result.stderr}")
            return False

    except FileNotFoundError:
        print("[ERROR] Docker Compose not found. Please install Docker Desktop.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to start Docker: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Wait for MongoDB to be ready")
    parser.add_argument("--host", default="localhost", help="MongoDB host (default: localhost)")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port (default: 27017)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--docker", action="store_true", help="Use Docker MongoDB (with auth)")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start Docker if not running")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")

    args = parser.parse_args()

    if not args.quiet:
        print("MongoDB Connection Checker")
        print("-" * 40)

    # Check what's available
    docker_status = check_docker_running()

    if args.docker or docker_status in ["healthy", "running"]:
        # Use Docker MongoDB
        if docker_status == "not_running" and args.auto_start:
            if not start_docker_mongo():
                sys.exit(1)
            # Wait a bit for container to initialize
            time.sleep(5)
            docker_status = check_docker_running()

        if docker_status in ["healthy", "running"]:
            if not args.quiet:
                print(f"[INFO] Using Docker MongoDB (status: {docker_status})")

            # Use authenticated connection for Docker
            if check_mongo_ready(args.host, args.port, auth=True, max_attempts=args.timeout):
                if not args.quiet:
                    print("[OK] MongoDB is ready for connections")
                sys.exit(0)
            else:
                print("[ERROR] MongoDB is not responding")
                sys.exit(1)
        else:
            print("[ERROR] Docker MongoDB container is not running")
            if not args.auto_start:
                print("       Use --auto-start to start it automatically")
            sys.exit(1)

    else:
        # Try local MongoDB
        if not args.quiet:
            print("[INFO] Checking for local MongoDB...")

        if check_local_mongo():
            if not args.quiet:
                print("[OK] Local MongoDB is ready")
            sys.exit(0)
        else:
            print("[ERROR] No MongoDB instance found")
            print("\nTo start MongoDB:")
            print("  Docker:  python scripts/wait_for_mongo.py --docker --auto-start")
            print("  Local:   Start MongoDB service manually")
            sys.exit(1)

if __name__ == "__main__":
    main()