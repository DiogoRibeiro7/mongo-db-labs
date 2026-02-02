#!/usr/bin/env python3
"""
Build index pages for MongoDB Labs by scanning lab.json metadata files.

This script automatically generates:
- README.md lab table section
- docs/LABS.md comprehensive lab catalog

Usage:
    python scripts/build_index.py           # Generate all indexes
    python scripts/build_index.py --check   # Check if indexes are up-to-date
    python scripts/build_index.py --format markdown|json|html
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Dict, Any
import hashlib


class LabIndexBuilder:
    """Build lab indexes from metadata files."""

    def __init__(self):
        """Initialize the index builder."""
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.labs_dir = self.project_root / "labs"
        self.docs_dir = self.project_root / "docs"

    def find_lab_metadata(self) -> List[Dict[str, Any]]:
        """Find and load all lab.json files."""
        labs = []

        for lab_dir in sorted(self.labs_dir.iterdir()):
            if not lab_dir.is_dir():
                continue

            # Check for lab.json or lab.yml
            metadata_file = lab_dir / "lab.json"
            if not metadata_file.exists():
                metadata_file = lab_dir / "lab.yml"

            if metadata_file.exists():
                try:
                    if metadata_file.suffix == ".json":
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    else:
                        # YAML support (optional)
                        try:
                            import yaml
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = yaml.safe_load(f)
                        except ImportError:
                            print(f"Warning: PyYAML not installed, skipping {metadata_file}")
                            continue

                    # Add directory name if slug not specified
                    if 'slug' not in metadata:
                        metadata['slug'] = lab_dir.name

                    labs.append(metadata)
                except Exception as e:
                    print(f"Error loading {metadata_file}: {e}")

        return labs

    def generate_readme_table(self, labs: List[Dict]) -> str:
        """Generate the lab table for README.md."""
        table_lines = [
            "| Lab Name | Slug | Difficulty | Key Topics | Collections | Domain |",
            "|----------|------|------------|------------|-------------|--------|"
        ]

        for lab in labs:
            name = lab.get('name', 'Unknown')
            slug = lab.get('slug', 'unknown')
            difficulty = lab.get('difficulty', 'unknown').capitalize()
            domain = lab.get('domain', 'General')

            # Format collections
            collections = lab.get('collections', [])
            if len(collections) > 3:
                collections_str = f"{len(collections)} ({', '.join(collections[:3])}, ...)"
            else:
                collections_str = f"{len(collections)} ({', '.join(collections)})"

            # Format key topics
            topics = lab.get('key_topics', [])
            if len(topics) > 3:
                topics_str = ', '.join(topics[:3]) + ', ...'
            else:
                topics_str = ', '.join(topics)

            row = f"| **{name}** | `{slug}` | {difficulty} | {topics_str} | {collections_str} | {domain} |"
            table_lines.append(row)

        return '\n'.join(table_lines)

    def generate_labs_md(self, labs: List[Dict]) -> str:
        """Generate comprehensive LABS.md documentation."""
        lines = [
            "# MongoDB Teaching Labs Catalog",
            "",
            f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## Overview",
            "",
            f"This repository contains **{len(labs)} teaching labs** for MongoDB, covering various domains and difficulty levels.",
            "",
            "## Quick Navigation",
            ""
        ]

        # Create navigation links
        for lab in labs:
            name = lab.get('name', 'Unknown')
            slug = lab.get('slug', 'unknown')
            lines.append(f"- [{name}](#{slug})")

        lines.extend([
            "",
            "---",
            "",
            "## Lab Details",
            ""
        ])

        # Add detailed section for each lab
        for lab in labs:
            lines.extend(self._generate_lab_section(lab))

        # Add statistics section
        lines.extend(self._generate_statistics(labs))

        return '\n'.join(lines)

    def _generate_lab_section(self, lab: Dict) -> List[str]:
        """Generate detailed section for a single lab."""
        lines = [
            f"### {lab.get('name', 'Unknown')} {{#{lab.get('slug', 'unknown')}}}",
            ""
        ]

        # Basic info
        lines.extend([
            f"**Slug:** `{lab.get('slug', 'unknown')}`",
            f"**Domain:** {lab.get('domain', 'General')}",
            f"**Difficulty:** {lab.get('difficulty', 'unknown').capitalize()}",
            f"**Database:** `{lab.get('database', 'unknown')}`",
            f"**Estimated Time:** {lab.get('estimated_time', 'N/A')}",
            ""
        ])

        # Learning outcomes
        if 'learning_outcomes' in lab:
            lines.extend([
                "#### Learning Outcomes",
                ""
            ])
            for outcome in lab['learning_outcomes']:
                lines.append(f"- {outcome}")
            lines.append("")

        # Collections
        if 'collections' in lab:
            collections = lab['collections']
            lines.extend([
                "#### Collections",
                "",
                f"{len(collections)} collections: `{('`, `'.join(collections))}`",
                ""
            ])

        # Key Topics
        if 'key_topics' in lab:
            lines.extend([
                "#### Key Topics",
                ""
            ])
            for topic in lab['key_topics']:
                lines.append(f"- {topic}")
            lines.append("")

        # Sensors (if applicable)
        if 'sensors' in lab and lab['sensors']:
            lines.extend([
                "#### Sensors/Metrics",
                "",
                ', '.join(f"`{sensor}`" for sensor in lab['sensors']),
                ""
            ])

        # Features
        if 'features' in lab:
            features = lab['features']
            enabled = [k.replace('_', ' ').title() for k, v in features.items() if v]
            if enabled:
                lines.extend([
                    "#### Features",
                    "",
                    '[✓] ' + ' | [✓] '.join(enabled),
                    ""
                ])

        # Files
        if 'files' in lab:
            files = lab['files']
            lines.extend([
                "#### Files",
                ""
            ])
            for file_type, filename in files.items():
                lines.append(f"- **{file_type.capitalize()}:** `{filename}`")
            lines.append("")

        # Prerequisites
        if 'prerequisites' in lab:
            lines.extend([
                "#### Prerequisites",
                ""
            ])
            for prereq in lab['prerequisites']:
                lines.append(f"- {prereq}")
            lines.append("")

        # Tags
        if 'tags' in lab:
            tags = ' '.join(f"`#{tag}`" for tag in lab['tags'])
            lines.extend([
                "#### Tags",
                "",
                tags,
                ""
            ])

        # Quick start
        slug = lab.get('slug', 'unknown')
        lines.extend([
            "#### Quick Start",
            "",
            "```bash",
            f"cd labs/{slug}",
            "mongosh 00_setup_mongodb.js",
            "python 01_seed_*.py",
            "python 02_simulate_*.py --hours 1",
            "mongosh 03_queries_exam.js",
            "```",
            "",
            "---",
            ""
        ])

        return lines

    def _generate_statistics(self, labs: List[Dict]) -> List[str]:
        """Generate statistics section."""
        lines = [
            "## Statistics",
            "",
            "### By Difficulty",
            ""
        ]

        # Count by difficulty
        difficulty_counts = {}
        for lab in labs:
            difficulty = lab.get('difficulty', 'unknown').capitalize()
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        for difficulty, count in sorted(difficulty_counts.items()):
            lines.append(f"- **{difficulty}:** {count} lab(s)")

        lines.extend(["", "### By Domain", ""])

        # Count by domain
        domain_counts = {}
        for lab in labs:
            domain = lab.get('domain', 'General')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        for domain, count in sorted(domain_counts.items()):
            lines.append(f"- **{domain}:** {count} lab(s)")

        lines.extend(["", "### Feature Coverage", ""])

        # Feature statistics
        feature_counts = {}
        for lab in labs:
            if 'features' in lab:
                for feature, enabled in lab['features'].items():
                    if enabled:
                        feature_name = feature.replace('_', ' ').title()
                        feature_counts[feature_name] = feature_counts.get(feature_name, 0) + 1

        for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(labs)) * 100
            lines.append(f"- **{feature}:** {count}/{len(labs)} labs ({percentage:.0f}%)")

        lines.extend(["", "### Total Metrics", ""])

        # Total collections
        total_collections = sum(len(lab.get('collections', [])) for lab in labs)
        lines.append(f"- **Total Labs:** {len(labs)}")
        lines.append(f"- **Total Collections:** {total_collections}")
        lines.append(f"- **Average Collections per Lab:** {total_collections/len(labs):.1f}")

        return lines

    def update_readme(self, table: str) -> bool:
        """Update README.md with new lab table."""
        readme_path = self.project_root / "README.md"

        if not readme_path.exists():
            print(f"Error: {readme_path} not found")
            return False

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the lab table section
        start_marker = "## 📚 Available Labs"
        end_marker = "## 🏗️ Repository Structure"

        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)

        if start_idx == -1 or end_idx == -1:
            print("Error: Could not find lab table markers in README.md")
            return False

        # Build new section
        new_section = f"{start_marker}\n\n{table}\n\n"

        # Replace section
        new_content = content[:start_idx] + new_section + content[end_idx:]

        # Write back
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    def generate_index_hash(self, labs: List[Dict]) -> str:
        """Generate hash of lab metadata for change detection."""
        # Create stable string representation
        labs_str = json.dumps(labs, sort_keys=True, indent=2)
        return hashlib.md5(labs_str.encode()).hexdigest()

    def check_if_outdated(self) -> bool:
        """Check if indexes need updating."""
        labs = self.find_lab_metadata()

        if not labs:
            print("No labs found with metadata")
            return False

        current_hash = self.generate_index_hash(labs)

        # Check if hash file exists
        hash_file = self.project_root / ".lab_index_hash"
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()

            if stored_hash == current_hash:
                return False  # Up to date
            else:
                return True  # Outdated
        else:
            return True  # No hash file, consider outdated

    def save_index_hash(self, labs: List[Dict]) -> None:
        """Save current index hash."""
        current_hash = self.generate_index_hash(labs)
        hash_file = self.project_root / ".lab_index_hash"

        with open(hash_file, 'w') as f:
            f.write(current_hash)

    def build(self, format='markdown', check_only=False) -> int:
        """Build the index."""
        labs = self.find_lab_metadata()

        if not labs:
            print("No labs found with metadata files (lab.json)")
            return 1

        print(f"Found {len(labs)} lab(s) with metadata")

        if check_only:
            if self.check_if_outdated():
                print("[ERROR] Lab index is outdated. Run 'python scripts/build_index.py' to update.")
                return 1
            else:
                print("[OK] Lab index is up-to-date")
                return 0

        # Generate README table
        table = self.generate_readme_table(labs)
        print("\nGenerated lab table for README.md")

        # Update README
        if self.update_readme(table):
            print("[OK] Updated README.md")
        else:
            print("[ERROR] Failed to update README.md")
            return 1

        # Generate LABS.md
        labs_md = self.generate_labs_md(labs)
        labs_md_path = self.docs_dir / "LABS.md"

        # Ensure docs directory exists
        self.docs_dir.mkdir(exist_ok=True)

        with open(labs_md_path, 'w', encoding='utf-8') as f:
            f.write(labs_md)
        print(f"[OK] Generated {labs_md_path}")

        # Save hash for change detection
        self.save_index_hash(labs)
        print("[OK] Saved index hash for change detection")

        # Additional formats (optional)
        if format == 'json':
            json_path = self.docs_dir / "labs.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(labs, f, indent=2)
            print(f"[OK] Generated {json_path}")

        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build lab index from metadata files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_index.py              # Build all indexes
  python scripts/build_index.py --check      # Check if up-to-date
  python scripts/build_index.py --format json # Also generate JSON
        """
    )

    parser.add_argument("--check", action="store_true",
                       help="Check if indexes are up-to-date")
    parser.add_argument("--format", choices=["markdown", "json", "html"],
                       default="markdown",
                       help="Output format (default: markdown)")

    args = parser.parse_args()

    builder = LabIndexBuilder()
    return builder.build(format=args.format, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())