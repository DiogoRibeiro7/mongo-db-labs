#!/usr/bin/env python3
"""
Simulation Script for E-commerce Order Management (OPTIONAL)

This script generates time-series data and events.
Delete this file if your lab doesn't need synthetic data generation.

This is typically used for:
- IoT sensor readings
- Transaction streams
- User activity logs
- System metrics

Replace {{PLACEHOLDERS}} with your specific values.
"""

import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Generator
import sys
import random
import time

try:
    from pymongo import MongoClient, InsertOne
    import pymongo
except ImportError:
    print("Error: pymongo not installed. Run: pip install pymongo")
    sys.exit(1)

# ============================================
# CONFIGURATION - REPLACE PLACEHOLDERS
# ============================================
DATABASE_NAME = "ecommerce_orders"  # e.g., "iot_flood_demo"
LAB_NAME = "E-commerce Order Management"

# Simulation parameters
DEFAULT_DURATION_HOURS = 24
DEFAULT_INTERVAL_SECONDS = 60


# ============================================
# Command Line Arguments
# ============================================
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Generate synthetic time-series data for {LAB_NAME}"
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
        "--hours",
        type=float,
        default=DEFAULT_DURATION_HOURS,
        help=f"Hours of data to generate (default: {DEFAULT_DURATION_HOURS})"
    )
    parser.add_argument(
        "--base-step-sec",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Base time interval in seconds (default: {DEFAULT_INTERVAL_SECONDS})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible data"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for bulk inserts (default: 1000)"
    )
    parser.add_argument(
        "--real-time",
        action="store_true",
        help="Simulate in real-time with delays"
    )
    return parser.parse_args()


# ============================================
# Data Generation Functions
# ============================================

def generate_sensor_reading(
    sensor_id: str,
    timestamp: datetime,
    base_value: float = 20.0,
    noise_factor: float = 2.0
) -> Dict[str, Any]:
    """
    Generate a single sensor reading.

    Example function - replace with your domain-specific logic.
    """
    # Simulate realistic patterns (e.g., daily cycles, random noise)
    hour_of_day = timestamp.hour
    daily_pattern = 5 * (1 + 0.5 * abs(12 - hour_of_day) / 12)  # Peak at noon
    random_noise = random.uniform(-noise_factor, noise_factor)

    value = base_value + daily_pattern + random_noise

    return {
        "ts": timestamp,
        "sensorId": sensor_id,
        "value": round(value, 2),
        "quality": random.choice(["good", "good", "good", "fair", "poor"]),  # Weighted
        "metadata": {
            "generated": True,
            "version": "1.0"
        }
    }


def generate_time_series(
    start_time: datetime,
    duration_hours: float,
    interval_seconds: int
) -> Generator[Dict[str, Any], None, None]:
    """
    Generate time-series data over a time period.

    Yields documents ready for insertion.
    """
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)

    # Example: Multiple sensors
    sensor_ids = ["SENSOR_001", "SENSOR_002", "SENSOR_003"]

    while current_time < end_time:
        # Generate reading for each sensor
        for sensor_id in sensor_ids:
            # Add some randomness to timing
            jitter = random.randint(-5, 5)
            reading_time = current_time + timedelta(seconds=jitter)

            yield generate_sensor_reading(sensor_id, reading_time)

        # Advance time
        current_time += timedelta(seconds=interval_seconds)


def generate_events(
    start_time: datetime,
    duration_hours: float,
    avg_events_per_hour: float = 10
) -> List[Dict[str, Any]]:
    """
    Generate random events over a time period.

    Example for event-driven data.
    """
    events = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)

    while current_time < end_time:
        # Poisson-like distribution for event timing
        interval = random.expovariate(avg_events_per_hour / 3600)
        current_time += timedelta(seconds=interval)

        if current_time >= end_time:
            break

        # Generate event
        event = {
            "eventType": random.choice(["type_a", "type_b", "type_c"]),
            "severity": random.choice(["low", "medium", "high"]),
            "timestamp": current_time,
            "details": {
                "source": f"source_{random.randint(1, 5)}",
                "value": random.random()
            }
        }
        events.append(event)

    return events


# ============================================
# Database Operations
# ============================================

def insert_batch(collection: pymongo.collection.Collection, batch: List[Dict], description: str = "documents"):
    """Insert a batch of documents with error handling."""
    try:
        if batch:
            result = collection.insert_many(batch, ordered=False)
            print(f"  ✓ Inserted {len(result.inserted_ids)} {description}")
    except pymongo.errors.BulkWriteError as e:
        # Handle duplicate key errors gracefully
        inserted = e.details.get('nInserted', 0)
        print(f"  ⚠ Inserted {inserted} {description} (some duplicates skipped)")


# ============================================
# Main Simulation
# ============================================

def main():
    """Main simulation function."""
    args = parse_args()

    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Random seed set to: {args.seed}")

    # Connect to MongoDB
    print(f"\n=== {LAB_NAME} Data Simulation ===")
    print(f"Connecting to MongoDB at {args.host}:{args.port}...")

    try:
        client = MongoClient(args.host, args.port, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        sys.exit(1)

    db = client[args.database]
    print(f"Using database: {args.database}")

    # Determine time range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=args.hours)

    print(f"\nGenerating data from {start_time.isoformat()} to {end_time.isoformat()}")
    print(f"Duration: {args.hours} hours")
    print(f"Base interval: {args.base_step_sec} seconds")

    # ============================================
    # Generate Time-Series Data
    # ============================================
    print("\n--- Generating Time-Series Data ---")

    # Example: Insert sensor readings
    readings_collection = db.measurements  # REPLACE with your collection

    batch = []
    count = 0

    for reading in generate_time_series(start_time, args.hours, args.base_step_sec):
        batch.append(reading)
        count += 1

        # Insert in batches
        if len(batch) >= args.batch_size:
            insert_batch(readings_collection, batch, "readings")
            batch = []

            # Optional: Real-time simulation delay
            if args.real_time:
                time.sleep(args.base_step_sec)

    # Insert remaining batch
    if batch:
        insert_batch(readings_collection, batch, "readings")

    print(f"Total readings generated: {count}")

    # ============================================
    # Generate Events (if applicable)
    # ============================================
    print("\n--- Generating Events ---")

    # Example: Generate random events
    events_collection = db.events  # REPLACE with your collection
    events = generate_events(start_time, args.hours)

    if events:
        insert_batch(events_collection, events, "events")
        print(f"Total events generated: {len(events)}")

    # ============================================
    # Update Derived Data (if needed)
    # ============================================
    print("\n--- Updating Derived Data ---")

    # Example: Update statistics, aggregates, etc.
    # update_statistics(db, start_time, end_time)

    # ============================================
    # Summary
    # ============================================
    print("\n--- Simulation Summary ---")
    for collection_name in ["measurements", "events"]:  # REPLACE with your collections
        if collection_name in db.list_collection_names():
            count = db[collection_name].count_documents({
                "ts": {"$gte": start_time, "$lte": end_time}
            })
            print(f"  {collection_name}: {count} documents in time range")

    print("\n✓ Simulation complete!")
    print("\nNext step:")
    print("Run: mongosh 03_queries_exam.js")

    # Close connection
    client.close()


if __name__ == "__main__":
    main()