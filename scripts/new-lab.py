#!/usr/bin/env python3
"""
Create a new MongoDB lab from the template.

Usage:
    python scripts/new-lab.py <lab-slug>

Example:
    python scripts/new-lab.py ecommerce-orders
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a new MongoDB lab from template"
    )
    parser.add_argument(
        "slug",
        help="Lab slug (directory name, e.g., 'iot-sensors')"
    )
    parser.add_argument(
        "--name",
        help="Human-readable lab name (default: derived from slug)"
    )
    parser.add_argument(
        "--database",
        help="Database name (default: slug with underscores)"
    )
    parser.add_argument(
        "--domain",
        help="Problem domain (e.g., 'IoT', 'E-commerce')"
    )
    parser.add_argument(
        "--author",
        default="Lab Author",
        help="Your name for attribution"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing lab directory"
    )
    return parser.parse_args()


def slug_to_name(slug):
    """Convert slug to human-readable name."""
    # Convert hyphens to spaces and capitalize words
    return " ".join(word.capitalize() for word in slug.split("-"))


def slug_to_database(slug):
    """Convert slug to database name."""
    # Replace hyphens with underscores
    return slug.replace("-", "_")


def replace_placeholders(file_path, replacements):
    """Replace placeholders in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"  [!] Warning: Could not process {file_path}: {e}")
        return False


def main():
    """Main execution."""
    args = parse_args()

    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    template_dir = project_root / "templates" / "lab"
    labs_dir = project_root / "labs"
    target_dir = labs_dir / args.slug

    # Check template exists
    if not template_dir.exists():
        print(f"[X] Template directory not found: {template_dir}")
        print("  Make sure you're running this from the project root.")
        sys.exit(1)

    # Check if target already exists
    if target_dir.exists() and not args.force:
        print(f"[X] Lab directory already exists: {target_dir}")
        print("  Use --force to overwrite or choose a different slug.")
        sys.exit(1)

    # Prepare replacements
    lab_name = args.name or slug_to_name(args.slug)
    database_name = args.database or slug_to_database(args.slug)
    domain = args.domain or "General"

    replacements = {
        "{{LAB_NAME}}": lab_name,
        "{{LAB_SLUG}}": args.slug,
        "{{DATABASE_NAME}}": database_name,
        "{{DOMAIN}}": domain,
        "{{YOUR_NAME}}": args.author,
        "{{CURRENT_DATE}}": datetime.now().strftime("%Y-%m-%d"),
        "{{DESCRIPTION}}": f"MongoDB lab for {domain.lower()} scenarios",
        "{{COLLECTIONS}}": "sites, sensors, measurements, events"  # Default
    }

    print(f"\n=== Creating New Lab: {lab_name} ===")
    print(f"Slug: {args.slug}")
    print(f"Database: {database_name}")
    print(f"Domain: {domain}")
    print(f"Target: {target_dir}")

    # Create labs directory if it doesn't exist
    labs_dir.mkdir(exist_ok=True)

    # Copy template to target
    if target_dir.exists():
        shutil.rmtree(target_dir)
        print(f"[OK] Removed existing directory")

    shutil.copytree(template_dir, target_dir)
    print(f"[OK] Copied template to {target_dir}")

    # Process all files to replace placeholders
    print("\nProcessing template files:")
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(target_dir)

            if file_path.suffix in ['.js', '.py', '.md', '.yml', '.txt', '.json']:
                if replace_placeholders(file_path, replacements):
                    print(f"  [OK] {relative_path}")

    # Create __init__.py if not exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"  [OK] Created __init__.py")

    # Print next steps
    print(f"\n[OK] Lab created successfully at: {target_dir}")
    print("\n--- Next Steps ---")
    print(f"1. Navigate to your lab:")
    print(f"   cd {target_dir.relative_to(Path.cwd())}")
    print(f"\n2. Customize the template files:")
    print(f"   - Define collections in 00_setup_mongodb.js")
    print(f"   - Add seed data in 01_seed_project.py")
    print(f"   - Create simulation in 02_simulate_project.py (or delete if not needed)")
    print(f"   - Write query exercises in 03_queries_exam.js")
    print(f"   - Document schema in DATABASE.md")
    print(f"   - Update README.md with lab specifics")
    print(f"\n3. Test your lab:")
    print(f"   mongosh 00_setup_mongodb.js")
    print(f"   python 01_seed_project.py")
    print(f"   mongosh 03_queries_exam.js")
    print(f"\n4. Update the main README:")
    print(f"   Add your lab to the table in {project_root / 'README.md'}")

    print("\n[OK] Happy teaching!")


if __name__ == "__main__":
    main()