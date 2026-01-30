#!/usr/bin/env python3
"""
Reset a MongoDB lab database to a clean state.

Usage:
    python scripts/reset-db.py <lab-slug> [options]

Example:
    python scripts/reset-db.py iot_flood_demo
    python scripts/reset-db.py iot_flood_demo --drop-database
"""

import sys
import argparse
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Reset a MongoDB lab database"
    )
    parser.add_argument(
        "lab",
        help="Lab slug/directory name (e.g., 'iot_flood_demo')"
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
        "--drop-database",
        action="store_true",
        help="Drop entire database (default: drop collections only)"
    )
    parser.add_argument(
        "--keep-master",
        action="store_true",
        help="Keep master data collections (sites, sensors, etc.)"
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        help="Specific collections to reset (default: all)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )
    return parser.parse_args()


def get_database_name(lab_slug):
    """Get database name from lab slug."""
    # Convert hyphens to underscores
    return lab_slug.replace("-", "_")


def connect_mongodb(host, port):
    """Connect to MongoDB."""
    try:
        from pymongo import MongoClient
        client = MongoClient(host, port, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        return client
    except ImportError:
        print("[X] Error: pymongo not installed")
        print("  Install with: pip install pymongo")
        sys.exit(1)
    except Exception as e:
        print(f"[X] Failed to connect to MongoDB at {host}:{port}")
        print(f"  Error: {e}")
        sys.exit(1)


def list_collections(db):
    """List all collections in database."""
    collections = db.list_collection_names()
    return sorted(collections)


def categorize_collections(collections):
    """Categorize collections into master and transactional."""
    # Common master data collection patterns
    master_patterns = [
        'sites', 'sensors', 'users', 'products', 'categories',
        'config', 'settings', 'metadata', 'policies', 'curves',
        'reference', 'lookup'
    ]

    master = []
    transactional = []

    for coll in collections:
        coll_lower = coll.lower()
        is_master = any(pattern in coll_lower for pattern in master_patterns)

        if is_master:
            master.append(coll)
        else:
            transactional.append(coll)

    return master, transactional


def main():
    """Main execution."""
    args = parse_args()

    # Get database name
    db_name = get_database_name(args.lab)

    print(f"\n{'='*50}")
    print(f"Reset MongoDB Lab Database")
    print(f"{'='*50}")
    print(f"Lab: {args.lab}")
    print(f"Database: {db_name}")
    print(f"MongoDB: {args.host}:{args.port}")

    # Connect to MongoDB
    print("\nConnecting to MongoDB...")
    client = connect_mongodb(args.host, args.port)
    db = client[db_name]
    print("[OK] Connected successfully")

    # Check if database exists
    if db_name not in client.list_database_names():
        print(f"\n[!] Database '{db_name}' does not exist")
        print("  Nothing to reset.")
        sys.exit(0)

    # List collections
    collections = list_collections(db)

    if not collections:
        print(f"\n[!] Database '{db_name}' has no collections")
        print("  Nothing to reset.")
        sys.exit(0)

    # Categorize collections
    master_colls, trans_colls = categorize_collections(collections)

    print(f"\nFound {len(collections)} collections:")
    if master_colls:
        print("\nMaster Data Collections:")
        for coll in master_colls:
            count = db[coll].count_documents({})
            print(f"  - {coll} ({count:,} documents)")

    if trans_colls:
        print("\nTransactional Collections:")
        for coll in trans_colls:
            count = db[coll].count_documents({})
            print(f"  - {coll} ({count:,} documents)")

    # Determine what to reset
    if args.drop_database:
        action = "DROP ENTIRE DATABASE"
        collections_to_reset = collections
    elif args.collections:
        # Specific collections
        collections_to_reset = [c for c in args.collections if c in collections]
        missing = [c for c in args.collections if c not in collections]
        if missing:
            print(f"\n[!] Warning: Collections not found: {', '.join(missing)}")
        action = f"RESET {len(collections_to_reset)} COLLECTIONS"
    elif args.keep_master:
        # Reset only transactional collections
        collections_to_reset = trans_colls
        action = f"RESET {len(collections_to_reset)} TRANSACTIONAL COLLECTIONS"
    else:
        # Reset all collections
        collections_to_reset = collections
        action = f"RESET ALL {len(collections_to_reset)} COLLECTIONS"

    if not collections_to_reset:
        print("\n[!] No collections to reset based on criteria")
        sys.exit(0)

    # Confirmation
    print(f"\n{'='*50}")
    print(f"[!] WARNING: This will {action}")
    print(f"{'='*50}")
    print("Collections to reset:")
    for coll in collections_to_reset[:10]:  # Show first 10
        print(f"  - {coll}")
    if len(collections_to_reset) > 10:
        print(f"  ... and {len(collections_to_reset) - 10} more")

    if not args.yes:
        response = input("\nAre you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("[X] Operation cancelled")
            sys.exit(0)

    # Perform reset
    print("\nResetting database...")

    if args.drop_database:
        # Drop entire database
        client.drop_database(db_name)
        print(f"[OK] Dropped database '{db_name}'")
    else:
        # Drop individual collections
        for coll in collections_to_reset:
            try:
                db[coll].drop()
                print(f"  [OK] Dropped collection: {coll}")
            except Exception as e:
                print(f"  [X] Failed to drop {coll}: {e}")

    # Summary
    print(f"\n{'='*50}")
    print("Reset Summary")
    print(f"{'='*50}")

    if args.drop_database:
        print(f"[OK] Database '{db_name}' has been dropped")
        print("\nTo recreate the database:")
    else:
        print(f"[OK] Reset {len(collections_to_reset)} collections")

        # Show what remains
        remaining = list_collections(db)
        if remaining:
            print(f"\nRemaining collections ({len(remaining)}):")
            for coll in remaining:
                count = db[coll].count_documents({})
                print(f"  - {coll} ({count:,} documents)")

        print("\nTo restore data:")

    # Next steps
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    lab_dir = project_root / "labs" / args.lab

    print(f"  cd {lab_dir.relative_to(Path.cwd())}")
    print("  mongosh 00_setup_mongodb.js")
    print("  python 01_seed_*.py")

    print("\n[OK] Reset complete!")

    # Close connection
    client.close()


if __name__ == "__main__":
    main()