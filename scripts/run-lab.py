#!/usr/bin/env python3
"""
Execute a complete MongoDB lab sequence.

Usage:
    python scripts/run-lab.py <lab-slug> [options]

Example:
    python scripts/run-lab.py iot_flood_demo --hours 24
    python scripts/run-lab.py iot_flood_demo --skip-setup --skip-seed
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a complete MongoDB lab sequence"
    )
    parser.add_argument(
        "lab",
        help="Lab slug/directory name (e.g., 'iot_flood_demo')"
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip database setup (00_setup_mongodb.js)"
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Skip data seeding (01_seed_*.py)"
    )
    parser.add_argument(
        "--skip-simulate",
        action="store_true",
        help="Skip simulation (02_simulate_*.py)"
    )
    parser.add_argument(
        "--skip-queries",
        action="store_true",
        help="Skip query exercises (03_queries_exam.js)"
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=24,
        help="Hours of data to simulate (default: 24)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible data"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="MongoDB host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=27017,
        help="MongoDB port (default: 27017)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing data before seeding"
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Start MongoDB using docker-compose first"
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop execution if any step fails"
    )
    return parser.parse_args()


def run_command(command, description, cwd=None, stop_on_error=False):
    """Run a shell command and handle output."""
    print(f"\n--- {description} ---")
    print(f"Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            return True
        else:
            print(f"[X] {description} failed with exit code {result.returncode}")
            if stop_on_error:
                sys.exit(result.returncode)
            return False

    except Exception as e:
        print(f"[X] Error running command: {e}")
        if stop_on_error:
            sys.exit(1)
        return False


def check_mongodb_connection(host, port):
    """Check if MongoDB is accessible."""
    try:
        import pymongo
        client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=5000)
        client.server_info()
        client.close()
        return True
    except:
        return False


def find_lab_files(lab_dir):
    """Find lab script files."""
    files = {}

    # Find setup script
    setup_files = list(lab_dir.glob("00_setup*.js"))
    if setup_files:
        files['setup'] = setup_files[0]

    # Find seed script
    seed_files = list(lab_dir.glob("01_seed*.py"))
    if seed_files:
        files['seed'] = seed_files[0]

    # Find simulation script
    simulate_files = list(lab_dir.glob("02_simulate*.py"))
    if simulate_files:
        files['simulate'] = simulate_files[0]

    # Find query script
    query_files = list(lab_dir.glob("03_queries*.js"))
    if query_files:
        files['queries'] = query_files[0]

    # Check for docker-compose
    docker_file = lab_dir / "docker-compose.yml"
    if docker_file.exists():
        files['docker'] = docker_file

    # Check for requirements
    requirements_file = lab_dir / "requirements.txt"
    if requirements_file.exists():
        files['requirements'] = requirements_file

    return files


def main():
    """Main execution."""
    args = parse_args()

    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    lab_dir = project_root / "labs" / args.lab

    # Check if lab exists
    if not lab_dir.exists():
        print(f"[X] Lab not found: {lab_dir}")
        print(f"\nAvailable labs:")
        labs_dir = project_root / "labs"
        if labs_dir.exists():
            for lab in labs_dir.iterdir():
                if lab.is_dir() and not lab.name.startswith('.'):
                    print(f"  - {lab.name}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"Running Lab: {args.lab}")
    print(f"{'='*50}")
    print(f"Lab directory: {lab_dir}")

    # Find lab files
    files = find_lab_files(lab_dir)

    if not files:
        print("[X] No lab scripts found in directory")
        sys.exit(1)

    print("\nFound lab files:")
    for key, path in files.items():
        print(f"  {key}: {path.name}")

    # Start Docker if requested
    if args.docker and 'docker' in files:
        run_command(
            "docker compose up -d",
            "Starting MongoDB with Docker",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )
        print("Waiting for MongoDB to be ready...")
        time.sleep(5)

    # Check MongoDB connection
    print(f"\nChecking MongoDB connection at {args.host}:{args.port}...")
    if check_mongodb_connection(args.host, args.port):
        print("[OK] MongoDB is accessible")
    else:
        print("[X] Cannot connect to MongoDB")
        print("  Make sure MongoDB is running on the specified host and port.")
        if args.stop_on_error:
            sys.exit(1)

    # Install Python requirements if needed
    if 'requirements' in files and ('seed' in files or 'simulate' in files):
        run_command(
            f"python -m pip install -r {files['requirements'].name}",
            "Installing Python dependencies",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )

    # Run setup script
    if not args.skip_setup and 'setup' in files:
        mongo_url = f"mongodb://{args.host}:{args.port}"
        run_command(
            f'mongosh "{mongo_url}" {files["setup"].name}',
            "Setting up database schema",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )

    # Run seed script
    if not args.skip_seed and 'seed' in files:
        seed_cmd = f"python {files['seed'].name} --host {args.host} --port {args.port}"
        if args.clean:
            seed_cmd += " --clean"
        if args.seed is not None:
            seed_cmd += f" --seed {args.seed}"

        run_command(
            seed_cmd,
            "Seeding master data",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )

    # Run simulation script
    if not args.skip_simulate and 'simulate' in files:
        sim_cmd = f"python {files['simulate'].name} --host {args.host} --port {args.port} --hours {args.hours}"
        if args.seed is not None:
            sim_cmd += f" --seed {args.seed}"

        run_command(
            sim_cmd,
            f"Simulating {args.hours} hours of data",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )

    # Run query exercises
    if not args.skip_queries and 'queries' in files:
        mongo_url = f"mongodb://{args.host}:{args.port}"
        run_command(
            f'mongosh "{mongo_url}" {files["queries"].name}',
            "Running query exercises",
            cwd=lab_dir,
            stop_on_error=args.stop_on_error
        )

    # Summary
    print(f"\n{'='*50}")
    print("Lab Execution Summary")
    print(f"{'='*50}")

    steps_run = []
    if not args.skip_setup and 'setup' in files:
        steps_run.append("Database setup")
    if not args.skip_seed and 'seed' in files:
        steps_run.append("Data seeding")
    if not args.skip_simulate and 'simulate' in files:
        steps_run.append(f"Simulation ({args.hours} hours)")
    if not args.skip_queries and 'queries' in files:
        steps_run.append("Query exercises")

    if steps_run:
        print("[OK] Completed steps:")
        for step in steps_run:
            print(f"  - {step}")
    else:
        print("[!] No steps were executed (all skipped)")

    print(f"\n[OK] Lab execution complete!")

    # Docker cleanup reminder
    if args.docker and 'docker' in files:
        print("\n--- Docker Cleanup ---")
        print("To stop MongoDB:")
        print(f"  cd {lab_dir.relative_to(Path.cwd())}")
        print("  docker compose down")
        print("\nTo stop and remove volumes:")
        print("  docker compose down -v")


if __name__ == "__main__":
    main()