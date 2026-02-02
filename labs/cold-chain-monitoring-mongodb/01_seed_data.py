#!/usr/bin/env python3
"""
Cold Chain Monitoring - Seed Script
Seeds master data for cold chain assets, sensors, and initial configurations
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
import random
import argparse

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "coldchain_db"


class ColdChainSeeder:
    """Seeds cold chain monitoring data."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize seeder with MongoDB connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

    def clean_collections(self):
        """Remove existing data from all collections."""
        collections = ["assets", "sensors", "events", "routes", "alerts"]
        for coll in collections:
            count = self.db[coll].delete_many({}).deleted_count
            if count > 0:
                print(f"Cleaned {count} documents from {coll}")

    def seed_assets(self):
        """Seed cold chain assets (fridges, freezers, trucks, containers)."""
        assets = []

        # Warehouse refrigerators
        for i in range(1, 6):
            assets.append({
                "assetId": f"FRG{100000 + i:06d}",
                "assetType": "refrigerator",
                "name": f"Warehouse Fridge #{i}",
                "status": "active",
                "location": {
                    "type": "Point",
                    "coordinates": [-122.4194 + random.uniform(-0.01, 0.01),
                                   37.7749 + random.uniform(-0.01, 0.01)],
                    "address": f"{1000 + i * 100} Market Street, San Francisco, CA"
                },
                "temperatureRange": {
                    "min": 2.0,
                    "max": 8.0,
                    "optimal": 4.0,
                    "unit": "C"
                },
                "capacity": {
                    "volume": 1000.0,
                    "unit": "L",
                    "currentLoad": random.uniform(30, 90)
                },
                "owner": {
                    "company": "FreshFoods Inc",
                    "contact": "John Smith",
                    "phone": "+1-555-0100"
                },
                "compliance": {
                    "certifications": ["FDA", "HACCP", "ISO22000"],
                    "lastInspection": datetime.now() - timedelta(days=random.randint(30, 90)),
                    "nextInspection": datetime.now() + timedelta(days=random.randint(30, 90))
                },
                "createdAt": datetime.now() - timedelta(days=365),
                "updatedAt": datetime.now() - timedelta(days=random.randint(1, 30))
            })

        # Medical freezers
        for i in range(1, 4):
            assets.append({
                "assetId": f"FRZ{200000 + i:06d}",
                "assetType": "freezer",
                "name": f"Medical Freezer #{i}",
                "status": "active",
                "location": {
                    "type": "Point",
                    "coordinates": [-122.4294 + random.uniform(-0.01, 0.01),
                                   37.7849 + random.uniform(-0.01, 0.01)],
                    "address": f"{2000 + i * 100} Mission Bay, San Francisco, CA"
                },
                "temperatureRange": {
                    "min": -80.0,
                    "max": -70.0,
                    "optimal": -75.0,
                    "unit": "C"
                },
                "capacity": {
                    "volume": 500.0,
                    "unit": "L",
                    "currentLoad": random.uniform(20, 70)
                },
                "owner": {
                    "company": "BioMed Solutions",
                    "contact": "Dr. Sarah Johnson",
                    "phone": "+1-555-0200"
                },
                "compliance": {
                    "certifications": ["FDA", "GMP", "CDC"],
                    "lastInspection": datetime.now() - timedelta(days=random.randint(15, 45)),
                    "nextInspection": datetime.now() + timedelta(days=random.randint(15, 45))
                },
                "createdAt": datetime.now() - timedelta(days=500),
                "updatedAt": datetime.now() - timedelta(days=random.randint(1, 15))
            })

        # Refrigerated trucks
        for i in range(1, 5):
            assets.append({
                "assetId": f"TRK{300000 + i:06d}",
                "assetType": "truck",
                "name": f"Delivery Truck #{i}",
                "status": random.choice(["active", "in_transit"]),
                "location": {
                    "type": "Point",
                    "coordinates": [-122.4094 + random.uniform(-0.05, 0.05),
                                   37.7549 + random.uniform(-0.05, 0.05)],
                    "address": "Mobile Unit"
                },
                "temperatureRange": {
                    "min": -2.0,
                    "max": 5.0,
                    "optimal": 2.0,
                    "unit": "C"
                },
                "capacity": {
                    "volume": 20.0,
                    "unit": "m3",
                    "currentLoad": random.uniform(0, 100)
                },
                "owner": {
                    "company": "ColdChain Logistics",
                    "contact": "Mike Wilson",
                    "phone": "+1-555-0300"
                },
                "compliance": {
                    "certifications": ["DOT", "FDA", "FSMA"],
                    "lastInspection": datetime.now() - timedelta(days=random.randint(7, 30)),
                    "nextInspection": datetime.now() + timedelta(days=random.randint(30, 60))
                },
                "createdAt": datetime.now() - timedelta(days=700),
                "updatedAt": datetime.now() - timedelta(hours=random.randint(1, 48))
            })

        # Shipping containers
        for i in range(1, 3):
            assets.append({
                "assetId": f"CTN{400000 + i:06d}",
                "assetType": "container",
                "name": f"Shipping Container #{i}",
                "status": random.choice(["active", "in_transit"]),
                "location": {
                    "type": "Point",
                    "coordinates": [-122.3894 + random.uniform(-0.02, 0.02),
                                   37.7949 + random.uniform(-0.02, 0.02)],
                    "address": "Port of San Francisco"
                },
                "temperatureRange": {
                    "min": -25.0,
                    "max": -18.0,
                    "optimal": -20.0,
                    "unit": "C"
                },
                "capacity": {
                    "volume": 33.0,
                    "unit": "m3",
                    "currentLoad": random.uniform(40, 95)
                },
                "owner": {
                    "company": "Global Shipping Co",
                    "contact": "Lisa Chen",
                    "phone": "+1-555-0400"
                },
                "compliance": {
                    "certifications": ["ISO", "IMO", "FDA"],
                    "lastInspection": datetime.now() - timedelta(days=random.randint(30, 120)),
                    "nextInspection": datetime.now() + timedelta(days=random.randint(30, 180))
                },
                "createdAt": datetime.now() - timedelta(days=400),
                "updatedAt": datetime.now() - timedelta(days=random.randint(1, 7))
            })

        result = self.db.assets.insert_many(assets)
        print(f"Seeded {len(result.inserted_ids)} assets")
        return assets

    def seed_sensors(self, assets):
        """Seed sensors for each asset."""
        sensors = []
        sensor_counter = 10000000

        for asset in assets:
            # Temperature sensors (2-3 per asset)
            num_temp_sensors = random.randint(2, 3)
            for i in range(num_temp_sensors):
                sensor_counter += 1
                sensors.append({
                    "sensorId": f"SEN{sensor_counter:08d}",
                    "assetId": asset["assetId"],
                    "sensorType": "temperature",
                    "model": random.choice(["TempTrack Pro", "CryoSense 2000", "ThermoGuard X"]),
                    "status": "active",
                    "position": ["top_shelf", "middle_shelf", "bottom_shelf", "door"][i],
                    "calibration": {
                        "offset": random.uniform(-0.5, 0.5),
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 180)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(30, 180))
                    },
                    "batteryLevel": random.randint(70, 100),
                    "installedAt": asset["createdAt"] + timedelta(days=random.randint(1, 30)),
                    "lastReading": datetime.now() - timedelta(minutes=random.randint(1, 60))
                })

            # Humidity sensor (50% chance)
            if random.random() > 0.5:
                sensor_counter += 1
                sensors.append({
                    "sensorId": f"SEN{sensor_counter:08d}",
                    "assetId": asset["assetId"],
                    "sensorType": "humidity",
                    "model": "HumidiTrack 500",
                    "status": "active",
                    "position": "center",
                    "calibration": {
                        "offset": random.uniform(-2, 2),
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(60, 240)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(60, 240))
                    },
                    "batteryLevel": random.randint(60, 100),
                    "installedAt": asset["createdAt"] + timedelta(days=random.randint(1, 60)),
                    "lastReading": datetime.now() - timedelta(minutes=random.randint(1, 120))
                })

            # Door sensor (for fridges/freezers)
            if asset["assetType"] in ["refrigerator", "freezer"]:
                sensor_counter += 1
                sensors.append({
                    "sensorId": f"SEN{sensor_counter:08d}",
                    "assetId": asset["assetId"],
                    "sensorType": "door",
                    "model": "DoorGuard Pro",
                    "status": "active",
                    "position": "door_frame",
                    "batteryLevel": random.randint(80, 100),
                    "installedAt": asset["createdAt"] + timedelta(days=random.randint(1, 30)),
                    "lastReading": datetime.now() - timedelta(minutes=random.randint(1, 30))
                })

            # GPS sensor (for trucks/containers)
            if asset["assetType"] in ["truck", "container"]:
                sensor_counter += 1
                sensors.append({
                    "sensorId": f"SEN{sensor_counter:08d}",
                    "assetId": asset["assetId"],
                    "sensorType": "gps",
                    "model": "TrackMaster 3000",
                    "status": "active",
                    "position": "roof",
                    "batteryLevel": random.randint(50, 100),
                    "installedAt": asset["createdAt"] + timedelta(days=random.randint(1, 30)),
                    "lastReading": datetime.now() - timedelta(minutes=random.randint(1, 15))
                })

        result = self.db.sensors.insert_many(sensors)
        print(f"Seeded {len(result.inserted_ids)} sensors")
        return sensors

    def seed_initial_events(self, assets):
        """Seed some initial events."""
        events = []
        event_counter = int(datetime.now().timestamp() * 1000)

        for asset in assets:
            # Recent door open/close events for fridges
            if asset["assetType"] in ["refrigerator", "freezer"]:
                for _ in range(random.randint(2, 5)):
                    event_counter += 1
                    open_time = datetime.now() - timedelta(
                        hours=random.randint(1, 48),
                        minutes=random.randint(0, 59)
                    )
                    close_time = open_time + timedelta(minutes=random.randint(1, 10))

                    events.append({
                        "eventId": f"EVT{event_counter:010d}",
                        "assetId": asset["assetId"],
                        "eventType": "door_open",
                        "timestamp": open_time,
                        "endTime": close_time,
                        "severity": "info",
                        "details": {
                            "duration_seconds": (close_time - open_time).total_seconds(),
                            "temperature_at_open": random.uniform(
                                asset["temperatureRange"]["min"],
                                asset["temperatureRange"]["max"]
                            )
                        },
                        "acknowledged": True,
                        "acknowledgedBy": "system",
                        "acknowledgedAt": close_time
                    })

            # Route events for trucks
            if asset["assetType"] == "truck" and asset["status"] == "in_transit":
                event_counter += 1
                events.append({
                    "eventId": f"EVT{event_counter:010d}",
                    "assetId": asset["assetId"],
                    "eventType": "route_start",
                    "timestamp": datetime.now() - timedelta(hours=random.randint(1, 6)),
                    "severity": "info",
                    "details": {
                        "origin": "Distribution Center",
                        "destination": "Retail Store",
                        "estimated_duration": random.randint(2, 8) * 3600
                    },
                    "acknowledged": True,
                    "acknowledgedBy": "dispatcher",
                    "acknowledgedAt": datetime.now() - timedelta(hours=random.randint(1, 5))
                })

        if events:
            result = self.db.events.insert_many(events)
            print(f"Seeded {len(result.inserted_ids)} initial events")
        return events

    def seed_routes(self, assets):
        """Seed transport routes for trucks and containers."""
        routes = []
        route_counter = 10000000

        transport_assets = [a for a in assets if a["assetType"] in ["truck", "container"]]

        for asset in transport_assets:
            # Create 1-2 routes per transport asset
            for _ in range(random.randint(1, 2)):
                route_counter += 1
                start_time = datetime.now() - timedelta(days=random.randint(0, 7))
                duration_hours = random.randint(2, 24)

                route_status = random.choice(["planned", "in_progress", "completed"])

                route = {
                    "routeId": f"RT{route_counter:08d}",
                    "assetId": asset["assetId"],
                    "status": route_status,
                    "origin": {
                        "name": random.choice(["Distribution Center", "Warehouse A", "Port Terminal"]),
                        "coordinates": [-122.4194 + random.uniform(-0.1, 0.1),
                                       37.7749 + random.uniform(-0.1, 0.1)]
                    },
                    "destination": {
                        "name": random.choice(["Retail Store", "Hospital", "Warehouse B"]),
                        "coordinates": [-122.4194 + random.uniform(-0.2, 0.2),
                                       37.7749 + random.uniform(-0.2, 0.2)]
                    },
                    "cargo": {
                        "description": random.choice([
                            "Pharmaceutical products",
                            "Fresh produce",
                            "Frozen seafood",
                            "Vaccines",
                            "Dairy products"
                        ]),
                        "quantity": random.randint(100, 1000),
                        "value": random.uniform(10000, 100000),
                        "temperatureRequirement": {
                            "min": asset["temperatureRange"]["min"],
                            "max": asset["temperatureRange"]["max"]
                        }
                    },
                    "startTime": start_time,
                    "expectedEndTime": start_time + timedelta(hours=duration_hours),
                    "distance": random.uniform(50, 500)
                }

                if route_status == "completed":
                    route["actualEndTime"] = start_time + timedelta(
                        hours=duration_hours + random.uniform(-1, 2)
                    )
                    route["duration"] = int(
                        (route["actualEndTime"] - start_time).total_seconds() / 60
                    )

                routes.append(route)

        if routes:
            result = self.db.routes.insert_many(routes)
            print(f"Seeded {len(result.inserted_ids)} routes")
        return routes

    def seed_initial_alerts(self, assets):
        """Seed some initial alerts."""
        alerts = []
        alert_counter = int(datetime.now().timestamp() * 1000)

        # Create a few sample alerts
        sample_assets = random.sample(assets, min(3, len(assets)))

        for asset in sample_assets:
            alert_counter += 1

            alert_type = random.choice([
                "temperature_high", "temperature_low",
                "door_open_too_long", "battery_low"
            ])

            alert = {
                "alertId": f"ALT{alert_counter:010d}",
                "assetId": asset["assetId"],
                "alertType": alert_type,
                "severity": random.choice(["low", "medium", "high"]),
                "status": random.choice(["active", "acknowledged", "resolved"]),
                "triggeredAt": datetime.now() - timedelta(
                    hours=random.randint(1, 72)
                ),
                "message": f"Alert: {alert_type.replace('_', ' ').title()} detected on {asset['name']}"
            }

            if alert_type in ["temperature_high", "temperature_low"]:
                is_high = alert_type == "temperature_high"
                threshold_value = asset["temperatureRange"]["max" if is_high else "min"]
                actual_value = threshold_value + (random.uniform(0.5, 3) if is_high else -random.uniform(0.5, 3))

                alert["threshold"] = {
                    "metric": "temperature",
                    "operator": ">" if is_high else "<",
                    "value": threshold_value,
                    "duration": random.randint(5, 30) * 60
                }
                alert["actualValue"] = actual_value

            if alert["status"] in ["acknowledged", "resolved"]:
                alert["acknowledgedAt"] = alert["triggeredAt"] + timedelta(
                    minutes=random.randint(5, 60)
                )
                alert["assignedTo"] = random.choice(["tech1", "tech2", "supervisor"])

            if alert["status"] == "resolved":
                alert["resolvedAt"] = alert["acknowledgedAt"] + timedelta(
                    minutes=random.randint(30, 180)
                )

            alerts.append(alert)

        if alerts:
            result = self.db.alerts.insert_many(alerts)
            print(f"Seeded {len(result.inserted_ids)} initial alerts")
        return alerts

    def run(self, clean=False):
        """Run the complete seeding process."""
        print("\n" + "="*50)
        print("Cold Chain Monitoring - Data Seeding")
        print("="*50)

        if clean:
            print("\nCleaning existing data...")
            self.clean_collections()

        print("\nSeeding master data...")

        # Seed assets first
        assets = self.seed_assets()

        # Seed dependent data
        sensors = self.seed_sensors(assets)
        events = self.seed_initial_events(assets)
        routes = self.seed_routes(assets)
        alerts = self.seed_initial_alerts(assets)

        print("\n" + "="*50)
        print("Seeding complete!")
        print(f"Database: {DB_NAME}")
        print(f"Assets: {len(assets)}")
        print(f"Sensors: {len(sensors)}")
        print(f"Events: {len(events)}")
        print(f"Routes: {len(routes)}")
        print(f"Alerts: {len(alerts)}")
        print("="*50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed cold chain monitoring data")
    parser.add_argument("--clean", action="store_true",
                      help="Clean existing data before seeding")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port")
    parser.add_argument("--database", default=DB_NAME, help="Database name")

    args = parser.parse_args()

    # Build MongoDB URI
    mongo_uri = f"mongodb://{args.host}:{args.port}"
    if os.environ.get("MONGO_URI"):
        mongo_uri = os.environ["MONGO_URI"]

    # Use database from argument or default
    db_name = args.database if args.database else DB_NAME

    # Run seeder
    seeder = ColdChainSeeder(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    seeder.run(clean=args.clean)


if __name__ == "__main__":
    main()