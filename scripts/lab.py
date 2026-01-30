#!/usr/bin/env python3
"""
MongoDB Teaching Labs Runner CLI

A lightweight command-line interface for managing MongoDB teaching labs.
No heavy dependencies - uses only standard library and subprocess.

Usage:
    python scripts/lab.py <command> [lab-name] [options]

Commands:
    list              List all available labs
    setup <lab>       Run database setup (00_setup_mongodb.js)
    seed <lab>        Run data seeding (01_seed_*.py)
    simulate <lab>    Run simulation (02_simulate_*.py)
    queries <lab>     Run query exercises (03_queries_exam.js)
    all <lab>         Run complete sequence (setup → seed → simulate → queries)
    validate <lab>    Check if lab structure is valid
    clean <lab>       Drop the lab's database

Environment Variables:
    MONGO_URI         MongoDB connection URI (default: mongodb://localhost:27017)
    MONGO_DB          Override database name (default: uses lab's configured name)

Examples:
    python scripts/lab.py list
    python scripts/lab.py all iot_flood_demo
    python scripts/lab.py seed soil_humidity_lorawan --clean
    MONGO_URI=mongodb://myserver:27017 python scripts/lab.py setup ecommerce-orders
"""

import os
import sys
import subprocess
import json
import glob
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'


class LabRunner:
    """Main lab runner class."""

    def __init__(self):
        """Initialize the lab runner."""
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.labs_dir = self.project_root / "labs"
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        self.mongo_db_override = os.environ.get("MONGO_DB", None)

    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

    def print_success(self, text: str) -> None:
        """Print a success message."""
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

    def print_error(self, text: str) -> None:
        """Print an error message."""
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {text}", file=sys.stderr)

    def print_warning(self, text: str) -> None:
        """Print a warning message."""
        print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {text}")

    def print_info(self, text: str) -> None:
        """Print an info message."""
        print(f"{Colors.CYAN}[INFO]{Colors.RESET} {text}")

    def print_step(self, step_num: int, total: int, description: str) -> None:
        """Print a step indicator."""
        print(f"\n{Colors.BOLD}Step {step_num}/{total}: {description}{Colors.RESET}")

    def check_mongosh(self) -> bool:
        """Check if mongosh is available."""
        try:
            result = subprocess.run(
                ["mongosh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def check_python(self) -> bool:
        """Check if Python is available and version is sufficient."""
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_available_labs(self) -> List[str]:
        """Get list of available labs."""
        labs = []
        if self.labs_dir.exists():
            for lab_dir in self.labs_dir.iterdir():
                if lab_dir.is_dir() and not lab_dir.name.startswith('.'):
                    # Check if it has at least the setup script
                    setup_script = lab_dir / "00_setup_mongodb.js"
                    if setup_script.exists():
                        labs.append(lab_dir.name)
        return sorted(labs)

    def get_lab_path(self, lab_name: str) -> Path:
        """Get the full path to a lab directory."""
        return self.labs_dir / lab_name

    def validate_lab_exists(self, lab_name: str) -> bool:
        """Check if a lab exists."""
        lab_path = self.get_lab_path(lab_name)
        if not lab_path.exists():
            self.print_error(f"Lab not found: {lab_name}")
            self.print_info("Available labs:")
            for lab in self.get_available_labs():
                print(f"  - {lab}")
            return False
        return True

    def get_database_name(self, lab_name: str) -> str:
        """Get the database name for a lab."""
        if self.mongo_db_override:
            return self.mongo_db_override

        # Try to extract from setup script
        lab_path = self.get_lab_path(lab_name)
        setup_script = lab_path / "00_setup_mongodb.js"

        if setup_script.exists():
            try:
                with open(setup_script, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for DATABASE_NAME constant
                    for line in content.split('\n'):
                        if 'DATABASE_NAME' in line and '=' in line:
                            # Extract value after = and before ;
                            parts = line.split('=')[1].split(';')[0].strip()
                            # Remove quotes
                            db_name = parts.strip('"\'')
                            if db_name and not db_name.startswith('{{'):
                                return db_name
            except Exception:
                pass

        # Default to lab name with underscores
        return lab_name.replace('-', '_')

    def run_command(self, command: List[str], cwd: Path = None, timeout: int = 300) -> Tuple[bool, str, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return False, "", f"Command not found: {command[0]}"
        except Exception as e:
            return False, "", str(e)

    def list_labs(self) -> int:
        """List all available labs."""
        self.print_header("Available MongoDB Teaching Labs")

        labs = self.get_available_labs()
        if not labs:
            self.print_warning("No labs found in the labs directory")
            return 1

        print(f"\nFound {len(labs)} lab(s):\n")

        for lab in labs:
            lab_path = self.get_lab_path(lab)
            db_name = self.get_database_name(lab)

            # Count files
            setup_exists = (lab_path / "00_setup_mongodb.js").exists()
            seed_scripts = list(lab_path.glob("01_seed_*.py"))
            sim_scripts = list(lab_path.glob("02_simulate_*.py"))
            query_exists = (lab_path / "03_queries_exam.js").exists()

            # Check documentation
            readme_exists = (lab_path / "README.md").exists()
            database_md_exists = (lab_path / "DATABASE.md").exists()

            print(f"{Colors.BOLD}{lab}{Colors.RESET}")
            print(f"  Database: {db_name}")
            print(f"  Scripts: ", end="")

            status_parts = []
            if setup_exists:
                status_parts.append(f"{Colors.GREEN}setup{Colors.RESET}")
            if seed_scripts:
                status_parts.append(f"{Colors.GREEN}seed{Colors.RESET}")
            if sim_scripts:
                status_parts.append(f"{Colors.GREEN}simulate{Colors.RESET}")
            else:
                status_parts.append(f"{Colors.YELLOW}simulate(optional){Colors.RESET}")
            if query_exists:
                status_parts.append(f"{Colors.GREEN}queries{Colors.RESET}")

            print(" | ".join(status_parts))

            if readme_exists and database_md_exists:
                print(f"  Docs: {Colors.GREEN}Complete{Colors.RESET}")
            else:
                print(f"  Docs: {Colors.YELLOW}Partial{Colors.RESET}")
            print()

        return 0

    def setup_lab(self, lab_name: str) -> int:
        """Run the setup script for a lab."""
        if not self.validate_lab_exists(lab_name):
            return 1

        if not self.check_mongosh():
            self.print_error("mongosh is not installed or not in PATH")
            self.print_info("Install MongoDB Shell from: https://www.mongodb.com/try/download/shell")
            return 1

        lab_path = self.get_lab_path(lab_name)
        setup_script = lab_path / "00_setup_mongodb.js"

        if not setup_script.exists():
            self.print_error(f"Setup script not found: {setup_script}")
            return 1

        self.print_header(f"Setting up lab: {lab_name}")
        db_name = self.get_database_name(lab_name)
        self.print_info(f"Database: {db_name}")
        self.print_info(f"MongoDB URI: {self.mongo_uri}")

        # Run mongosh with the setup script
        command = [
            "mongosh",
            self.mongo_uri,
            "--quiet",
            str(setup_script)
        ]

        self.print_info("Running setup script...")
        success, stdout, stderr = self.run_command(command, cwd=lab_path)

        if success:
            self.print_success("Setup completed successfully")
            if stdout and '--quiet' not in command:
                print(stdout)
            return 0
        else:
            self.print_error("Setup failed")
            if stderr:
                print(stderr, file=sys.stderr)
            return 1

    def seed_lab(self, lab_name: str, clean: bool = False) -> int:
        """Run the seed script for a lab."""
        if not self.validate_lab_exists(lab_name):
            return 1

        lab_path = self.get_lab_path(lab_name)
        seed_scripts = list(lab_path.glob("01_seed_*.py"))

        if not seed_scripts:
            self.print_error(f"No seed script found in {lab_path}")
            return 1

        seed_script = seed_scripts[0]  # Use the first one found

        self.print_header(f"Seeding lab: {lab_name}")
        db_name = self.get_database_name(lab_name)
        self.print_info(f"Database: {db_name}")
        self.print_info(f"Script: {seed_script.name}")

        # Parse MongoDB URI to get host and port
        host = "localhost"
        port = 27017
        if "://" in self.mongo_uri:
            try:
                # Simple parsing for host:port
                parts = self.mongo_uri.split("://")[1].split("/")[0]
                if ":" in parts:
                    host, port_str = parts.split(":")
                    port = int(port_str)
                else:
                    host = parts
            except:
                pass  # Use defaults if parsing fails

        # Build command
        command = [
            sys.executable,
            str(seed_script),
            "--host", host,
            "--port", str(port),
            "--database", db_name
        ]

        if clean:
            command.append("--clean")
            self.print_info("Clean mode: existing data will be removed")

        # Check if requirements.txt exists and suggest installation
        requirements = lab_path / "requirements.txt"
        if requirements.exists():
            self.print_warning(f"Note: This lab has Python dependencies in {requirements}")
            self.print_info("If the script fails, run: pip install -r requirements.txt")

        self.print_info("Running seed script...")
        success, stdout, stderr = self.run_command(command, cwd=lab_path, timeout=120)

        if success:
            self.print_success("Seeding completed successfully")
            if stdout:
                print(stdout)
            return 0
        else:
            self.print_error("Seeding failed")
            if stderr:
                print(stderr, file=sys.stderr)
            if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                self.print_warning("Missing Python dependencies. Run: pip install pymongo")
            return 1

    def simulate_lab(self, lab_name: str, hours: float = 24, seed: int = None) -> int:
        """Run the simulation script for a lab."""
        if not self.validate_lab_exists(lab_name):
            return 1

        lab_path = self.get_lab_path(lab_name)
        sim_scripts = list(lab_path.glob("02_simulate_*.py"))

        if not sim_scripts:
            self.print_warning(f"No simulation script found in {lab_path}")
            self.print_info("Simulation is optional - skipping")
            return 0

        sim_script = sim_scripts[0]  # Use the first one found

        self.print_header(f"Simulating lab: {lab_name}")
        db_name = self.get_database_name(lab_name)
        self.print_info(f"Database: {db_name}")
        self.print_info(f"Script: {sim_script.name}")
        self.print_info(f"Duration: {hours} hours")

        # Parse MongoDB URI to get host and port
        host = "localhost"
        port = 27017
        if "://" in self.mongo_uri:
            try:
                parts = self.mongo_uri.split("://")[1].split("/")[0]
                if ":" in parts:
                    host, port_str = parts.split(":")
                    port = int(port_str)
                else:
                    host = parts
            except:
                pass

        # Build command
        command = [
            sys.executable,
            str(sim_script),
            "--host", host,
            "--port", str(port),
            "--database", db_name,
            "--hours", str(hours)
        ]

        if seed is not None:
            command.extend(["--seed", str(seed)])
            self.print_info(f"Random seed: {seed}")

        self.print_info("Running simulation script...")
        self.print_warning("This may take a while for large datasets...")

        success, stdout, stderr = self.run_command(command, cwd=lab_path, timeout=600)

        if success:
            self.print_success("Simulation completed successfully")
            if stdout:
                print(stdout)
            return 0
        else:
            self.print_error("Simulation failed")
            if stderr:
                print(stderr, file=sys.stderr)
            return 1

    def run_queries(self, lab_name: str) -> int:
        """Run the query exercises for a lab."""
        if not self.validate_lab_exists(lab_name):
            return 1

        if not self.check_mongosh():
            self.print_error("mongosh is not installed or not in PATH")
            return 1

        lab_path = self.get_lab_path(lab_name)
        query_script = lab_path / "03_queries_exam.js"

        if not query_script.exists():
            self.print_error(f"Query script not found: {query_script}")
            return 1

        self.print_header(f"Running queries for lab: {lab_name}")
        db_name = self.get_database_name(lab_name)
        self.print_info(f"Database: {db_name}")

        # Run mongosh with the query script
        command = [
            "mongosh",
            self.mongo_uri,
            "--quiet",
            str(query_script)
        ]

        self.print_info("Running query exercises...")
        success, stdout, stderr = self.run_command(command, cwd=lab_path, timeout=120)

        if success:
            self.print_success("Queries executed successfully")
            if stdout:
                print(stdout)
            return 0
        else:
            self.print_error("Query execution failed")
            if stderr:
                print(stderr, file=sys.stderr)
            return 1

    def run_all(self, lab_name: str, clean: bool = False, hours: float = 24, seed: int = None) -> int:
        """Run the complete sequence for a lab."""
        self.print_header(f"Running complete sequence for: {lab_name}")

        if not self.validate_lab_exists(lab_name):
            return 1

        total_steps = 4
        current_step = 0

        # Step 1: Setup
        current_step += 1
        self.print_step(current_step, total_steps, "Database Setup")
        if self.setup_lab(lab_name) != 0:
            self.print_error("Setup failed - stopping sequence")
            return 1
        time.sleep(1)  # Small delay between steps

        # Step 2: Seed
        current_step += 1
        self.print_step(current_step, total_steps, "Seeding Data")
        if self.seed_lab(lab_name, clean=clean) != 0:
            self.print_error("Seeding failed - stopping sequence")
            return 1
        time.sleep(1)

        # Step 3: Simulate (optional)
        current_step += 1
        self.print_step(current_step, total_steps, "Running Simulation")
        # Don't fail if simulation doesn't exist or fails
        self.simulate_lab(lab_name, hours=hours, seed=seed)
        time.sleep(1)

        # Step 4: Queries
        current_step += 1
        self.print_step(current_step, total_steps, "Executing Queries")
        if self.run_queries(lab_name) != 0:
            self.print_error("Query execution failed")
            return 1

        self.print_header("Sequence Complete!")
        self.print_success(f"Lab '{lab_name}' is ready for use")
        self.print_info(f"Database: {self.get_database_name(lab_name)}")
        self.print_info(f"Connection: {self.mongo_uri}")

        return 0

    def validate_lab(self, lab_name: str) -> int:
        """Validate lab structure and requirements."""
        if not self.validate_lab_exists(lab_name):
            return 1

        self.print_header(f"Validating lab: {lab_name}")

        lab_path = self.get_lab_path(lab_name)
        issues = []
        warnings = []

        # Check required files
        required_files = [
            "00_setup_mongodb.js",
            "03_queries_exam.js",
            "README.md",
            "DATABASE.md"
        ]

        for file in required_files:
            file_path = lab_path / file
            if not file_path.exists():
                issues.append(f"Missing required file: {file}")
            else:
                self.print_success(f"Found: {file}")

        # Check for seed script
        seed_scripts = list(lab_path.glob("01_seed_*.py"))
        if not seed_scripts:
            issues.append("No seed script found (01_seed_*.py)")
        else:
            self.print_success(f"Found seed script: {seed_scripts[0].name}")

        # Check for simulation script (optional)
        sim_scripts = list(lab_path.glob("02_simulate_*.py"))
        if not sim_scripts:
            warnings.append("No simulation script found (02_simulate_*.py) - this is optional")
        else:
            self.print_success(f"Found simulation script: {sim_scripts[0].name}")

        # Check optional files
        optional_files = ["docker-compose.yml", "requirements.txt"]
        for file in optional_files:
            file_path = lab_path / file
            if file_path.exists():
                self.print_success(f"Found optional: {file}")

        # Check database name
        db_name = self.get_database_name(lab_name)
        self.print_info(f"Database name: {db_name}")

        # Print results
        print()
        if issues:
            self.print_error(f"Validation failed with {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            self.print_success("Validation passed - all required files present")

        if warnings:
            print()
            for warning in warnings:
                self.print_warning(warning)

        return 1 if issues else 0

    def clean_lab(self, lab_name: str) -> int:
        """Drop the database for a lab."""
        if not self.validate_lab_exists(lab_name):
            return 1

        if not self.check_mongosh():
            self.print_error("mongosh is not installed or not in PATH")
            return 1

        db_name = self.get_database_name(lab_name)

        self.print_header(f"Cleaning lab: {lab_name}")
        self.print_warning(f"This will DROP the database: {db_name}")

        # Confirm
        response = input(f"\nAre you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            self.print_info("Cancelled")
            return 0

        # Drop database using mongosh
        command = [
            "mongosh",
            self.mongo_uri,
            "--quiet",
            "--eval",
            f"db.getSiblingDB('{db_name}').dropDatabase()"
        ]

        self.print_info("Dropping database...")
        success, stdout, stderr = self.run_command(command)

        if success:
            self.print_success(f"Database '{db_name}' dropped successfully")
            return 0
        else:
            self.print_error("Failed to drop database")
            if stderr:
                print(stderr, file=sys.stderr)
            return 1


def main():
    """Main entry point."""
    runner = LabRunner()

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="MongoDB Teaching Labs Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/lab.py list
  python scripts/lab.py all iot_flood_demo
  python scripts/lab.py seed soil_humidity_lorawan --clean
  python scripts/lab.py simulate ecommerce-orders --hours 48
  MONGO_URI=mongodb://myserver:27017 python scripts/lab.py setup mylab
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    subparsers.add_parser('list', help='List all available labs')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Run database setup')
    setup_parser.add_argument('lab', help='Lab name')

    # Seed command
    seed_parser = subparsers.add_parser('seed', help='Run data seeding')
    seed_parser.add_argument('lab', help='Lab name')
    seed_parser.add_argument('--clean', action='store_true', help='Clean existing data first')

    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run simulation')
    sim_parser.add_argument('lab', help='Lab name')
    sim_parser.add_argument('--hours', type=float, default=24, help='Hours to simulate (default: 24)')
    sim_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Queries command
    queries_parser = subparsers.add_parser('queries', help='Run query exercises')
    queries_parser.add_argument('lab', help='Lab name')

    # All command
    all_parser = subparsers.add_parser('all', help='Run complete sequence')
    all_parser.add_argument('lab', help='Lab name')
    all_parser.add_argument('--clean', action='store_true', help='Clean existing data first')
    all_parser.add_argument('--hours', type=float, default=24, help='Hours to simulate (default: 24)')
    all_parser.add_argument('--seed', type=int, help='Random seed for simulation')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate lab structure')
    validate_parser.add_argument('lab', help='Lab name')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Drop lab database')
    clean_parser.add_argument('lab', help='Lab name')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        if args.command == 'list':
            return runner.list_labs()
        elif args.command == 'setup':
            return runner.setup_lab(args.lab)
        elif args.command == 'seed':
            return runner.seed_lab(args.lab, clean=args.clean)
        elif args.command == 'simulate':
            return runner.simulate_lab(args.lab, hours=args.hours, seed=args.seed)
        elif args.command == 'queries':
            return runner.run_queries(args.lab)
        elif args.command == 'all':
            return runner.run_all(args.lab, clean=args.clean, hours=args.hours, seed=args.seed)
        elif args.command == 'validate':
            return runner.validate_lab(args.lab)
        elif args.command == 'clean':
            return runner.clean_lab(args.lab)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR]{Colors.RESET} Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())