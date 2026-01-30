#!/usr/bin/env python3
"""
Seed Script for E-commerce Order Management

This script populates the database with master/reference data.
This includes static or slowly-changing data like:
- Configuration
- Reference tables
- Initial state

Replace {{PLACEHOLDERS}} with your specific values.
"""

import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any
import sys

try:
    from pymongo import MongoClient
    import pymongo
except ImportError:
    print("Error: pymongo not installed. Run: pip install pymongo")
    sys.exit(1)

# ============================================
# CONFIGURATION - REPLACE PLACEHOLDERS
# ============================================
DATABASE_NAME = "ecommerce_orders"  # e.g., "iot_flood_demo"
LAB_NAME = "E-commerce Order Management"


# ============================================
# Command Line Arguments
# ============================================
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Seed master data for {LAB_NAME}"
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
        "--database",
        default=DATABASE_NAME,
        help=f"Database name (default: {DATABASE_NAME})"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing data before seeding"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible data"
    )
    return parser.parse_args()


# ============================================
# Seeding Functions
# ============================================

def seed_example_collection(db: pymongo.database.Database, clean: bool = False):
    """
    Seed example collection with master data.

    Replace this with your actual seeding logic.
    """
    collection = db.example

    if clean:
        result = collection.delete_many({})
        print(f"  Cleaned {result.deleted_count} documents from example collection")

    # Check if already seeded
    if collection.count_documents({}) > 0:
        print(f"  Example collection already has {collection.count_documents({})} documents")
        return

    # Example data - REPLACE WITH YOUR DATA
    documents = [
        {
            "code": "ITEM_001",
            "name": "Example Item 1",
            "category": "category_a",
            "status": "active",
            "metadata": {
                "created_by": "seed_script",
                "version": "1.0"
            },
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        },
        {
            "code": "ITEM_002",
            "name": "Example Item 2",
            "category": "category_b",
            "status": "active",
            "metadata": {
                "created_by": "seed_script",
                "version": "1.0"
            },
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
    ]

    # Insert data
    result = collection.insert_many(documents)
    print(f"  ✓ Inserted {len(result.inserted_ids)} documents into example collection")

    # Create any necessary references
    # e.g., store IDs for use in other collections
    return {doc["code"]: _id for doc, _id in zip(documents, result.inserted_ids)}


def seed_another_collection(db: pymongo.database.Database, clean: bool = False, refs: Dict = None):
    """
    Seed another collection that may reference the first.

    Add more seeding functions as needed.
    """
    # Your seeding logic here
    pass


# ============================================
# Data Generation Helpers
# ============================================

def generate_sample_data(count: int, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate sample data with optional random seed.

    Example helper function - customize as needed.
    """
    import random

    if seed is not None:
        random.seed(seed)

    data = []
    for i in range(count):
        data.append({
            "index": i,
            "value": random.random(),
            "category": random.choice(["A", "B", "C"]),
            "timestamp": datetime.now(timezone.utc)
        })

    return data


# ============================================
# Main Execution
# ============================================

def main():
    """Main execution function."""
    args = parse_args()

    # Connect to MongoDB
    print(f"\n=== Seeding {LAB_NAME} Database ===")
    print(f"Connecting to MongoDB at {args.host}:{args.port}...")

    try:
        client = MongoClient(args.host, args.port, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        sys.exit(1)

    db = client[args.database]
    print(f"Using database: {args.database}")

    # Set random seed if provided
    if args.seed is not None:
        import random
        random.seed(args.seed)
        print(f"Random seed set to: {args.seed}")

    # Seed collections in order (respect dependencies)
    print("\n--- Seeding Collections ---")

    # Example: Seed independent collections first
    refs = seed_example_collection(db, clean=args.clean)

    # Example: Seed dependent collections with references
    # seed_another_collection(db, clean=args.clean, refs=refs)

    # ADD YOUR SEEDING FUNCTIONS HERE
    # seed_your_collection(db, clean=args.clean)

    # Print summary
    print("\n--- Seeding Summary ---")
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"  {collection_name}: {count} documents")

    print("\n✓ Seeding complete!")
    print("\nNext steps:")
    print("1. Run: python 02_simulate_project.py (if applicable)")
    print("2. Run: mongosh 03_queries_exam.js")

    # Close connection
    client.close()


if __name__ == "__main__":
    main()