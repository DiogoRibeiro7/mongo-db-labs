#!/usr/bin/env python3
"""
Smart Parking Occupancy - Infrastructure Seeding Script
Seeds zones, parking spots, and sensors
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB connection settings
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "smartparking_db"


class SmartParkingSeeder:
    """Seeds smart parking infrastructure data."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize seeder with MongoDB connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

    def clean_collections(self):
        """Remove existing data from all collections."""
        collections = ["zones", "parking_spots", "sensors", "events", "violations"]
        for coll in collections:
            count = self.db[coll].delete_many({}).deleted_count
            if count > 0:
                print(f"Cleaned {count} documents from {coll}")

    def seed_zones(self):
        """Seed parking zones."""
        zones = []

        # Downtown zones
        downtown_zones = [
            {
                "zoneId": f"ZONE{1001:04d}",
                "name": "Downtown Central Plaza",
                "type": "street",
                "location": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.4194, 37.7749],
                        [-122.4180, 37.7749],
                        [-122.4180, 37.7735],
                        [-122.4194, 37.7735],
                        [-122.4194, 37.7749]
                    ]],
                    "address": "100-200 Market Street",
                    "city": "San Francisco",
                    "district": "Financial District"
                },
                "totalSpots": 45,
                "reservedSpots": {
                    "disabled": 3,
                    "electric": 5,
                    "loading": 2
                },
                "pricing": {
                    "currency": "USD",
                    "perHour": 4.50,
                    "perDay": 35.00,
                    "freeMinutes": 10,
                    "maxDailyCharge": 35.00,
                    "peakHourMultiplier": 1.5
                },
                "regulations": {
                    "maxStayHours": 4,
                    "operatingHours": {
                        "start": "08:00",
                        "end": "22:00"
                    },
                    "permitRequired": False,
                    "restrictions": ["No overnight parking", "Street cleaning Wed 6-8am"]
                },
                "features": ["surveillance", "lighting", "payment_app"],
                "createdAt": datetime.now() - timedelta(days=365)
            },
            {
                "zoneId": f"ZONE{1002:04d}",
                "name": "City Hall Garage",
                "type": "garage",
                "location": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.4200, 37.7755],
                        [-122.4190, 37.7755],
                        [-122.4190, 37.7745],
                        [-122.4200, 37.7745],
                        [-122.4200, 37.7755]
                    ]],
                    "address": "355 McAllister Street",
                    "city": "San Francisco",
                    "district": "Civic Center"
                },
                "totalSpots": 320,
                "reservedSpots": {
                    "disabled": 15,
                    "electric": 20,
                    "vip": 10
                },
                "pricing": {
                    "currency": "USD",
                    "perHour": 3.00,
                    "perDay": 25.00,
                    "freeMinutes": 15,
                    "maxDailyCharge": 25.00,
                    "peakHourMultiplier": 1.2
                },
                "regulations": {
                    "maxStayHours": 24,
                    "operatingHours": {
                        "start": "00:00",
                        "end": "23:59"
                    },
                    "permitRequired": False,
                    "restrictions": []
                },
                "features": ["covered", "surveillance", "lighting", "ev_charging", "payment_app"],
                "createdAt": datetime.now() - timedelta(days=730)
            }
        ]

        # Shopping district zones
        shopping_zones = [
            {
                "zoneId": f"ZONE{2001:04d}",
                "name": "Westfield Shopping Center",
                "type": "lot",
                "location": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.4070, 37.7840],
                        [-122.4050, 37.7840],
                        [-122.4050, 37.7820],
                        [-122.4070, 37.7820],
                        [-122.4070, 37.7840]
                    ]],
                    "address": "865 Market Street",
                    "city": "San Francisco",
                    "district": "Union Square"
                },
                "totalSpots": 180,
                "reservedSpots": {
                    "disabled": 10,
                    "electric": 15,
                    "vip": 5
                },
                "pricing": {
                    "currency": "USD",
                    "perHour": 5.00,
                    "perDay": 40.00,
                    "freeMinutes": 30,
                    "maxDailyCharge": 40.00,
                    "peakHourMultiplier": 1.3
                },
                "regulations": {
                    "maxStayHours": 8,
                    "operatingHours": {
                        "start": "07:00",
                        "end": "23:00"
                    },
                    "permitRequired": False,
                    "restrictions": ["3-hour free parking with validation"]
                },
                "features": ["covered", "surveillance", "lighting", "ev_charging", "valet"],
                "createdAt": datetime.now() - timedelta(days=500)
            }
        ]

        # Residential zones
        residential_zones = [
            {
                "zoneId": f"ZONE{3001:04d}",
                "name": "Mission District Street Parking",
                "type": "street",
                "location": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.4220, 37.7600],
                        [-122.4200, 37.7600],
                        [-122.4200, 37.7580],
                        [-122.4220, 37.7580],
                        [-122.4220, 37.7600]
                    ]],
                    "address": "Valencia Street",
                    "city": "San Francisco",
                    "district": "Mission"
                },
                "totalSpots": 65,
                "reservedSpots": {
                    "disabled": 4
                },
                "pricing": {
                    "currency": "USD",
                    "perHour": 2.00,
                    "perDay": 15.00,
                    "freeMinutes": 0,
                    "maxDailyCharge": 15.00,
                    "peakHourMultiplier": 1.0
                },
                "regulations": {
                    "maxStayHours": 2,
                    "operatingHours": {
                        "start": "09:00",
                        "end": "18:00"
                    },
                    "permitRequired": True,
                    "restrictions": ["Resident permit required after 6pm", "Street cleaning Mon 8-10am"]
                },
                "features": ["lighting"],
                "createdAt": datetime.now() - timedelta(days=900)
            }
        ]

        # Airport/transit zones
        transit_zones = [
            {
                "zoneId": f"ZONE{4001:04d}",
                "name": "BART Station Park & Ride",
                "type": "lot",
                "location": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.3920, 37.7900],
                        [-122.3900, 37.7900],
                        [-122.3900, 37.7880],
                        [-122.3920, 37.7880],
                        [-122.3920, 37.7900]
                    ]],
                    "address": "BART Powell Street Station",
                    "city": "San Francisco",
                    "district": "Downtown"
                },
                "totalSpots": 250,
                "reservedSpots": {
                    "disabled": 12,
                    "electric": 8
                },
                "pricing": {
                    "currency": "USD",
                    "perHour": 2.50,
                    "perDay": 12.00,
                    "freeMinutes": 0,
                    "maxDailyCharge": 12.00,
                    "peakHourMultiplier": 1.0
                },
                "regulations": {
                    "maxStayHours": 24,
                    "operatingHours": {
                        "start": "05:00",
                        "end": "01:00"
                    },
                    "permitRequired": False,
                    "restrictions": ["No overnight parking 1am-5am"]
                },
                "features": ["surveillance", "lighting", "payment_app"],
                "createdAt": datetime.now() - timedelta(days=1200)
            }
        ]

        zones.extend(downtown_zones)
        zones.extend(shopping_zones)
        zones.extend(residential_zones)
        zones.extend(transit_zones)

        # Insert zones
        if zones:
            result = self.db.zones.insert_many(zones)
            print(f"Seeded {len(result.inserted_ids)} zones")

        return zones

    def seed_parking_spots(self, zones):
        """Seed individual parking spots for each zone."""
        parking_spots = []
        spot_counter = 1

        for zone in zones:
            zone_spots = zone["totalSpots"]
            reserved = zone.get("reservedSpots", {})

            # Calculate regular spots
            special_spots = sum([
                reserved.get("disabled", 0),
                reserved.get("electric", 0),
                reserved.get("vip", 0),
                reserved.get("loading", 0)
            ])
            regular_spots = zone_spots - special_spots

            # Base coordinates for the zone (using first point of polygon)
            base_coords = zone["location"]["coordinates"][0][0]

            # Create disabled spots
            for i in range(reserved.get("disabled", 0)):
                parking_spots.append({
                    "spotId": f"SPOT{spot_counter:08d}",
                    "zoneId": zone["zoneId"],
                    "spotNumber": f"H-{i+1:02d}",
                    "type": "disabled",
                    "status": random.choice(["available", "occupied", "occupied"]),
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            base_coords[0] + random.uniform(-0.0001, 0.0001),
                            base_coords[1] + random.uniform(-0.0001, 0.0001)
                        ],
                        "level": 0 if zone["type"] != "garage" else random.randint(0, 3),
                        "section": "A"
                    },
                    "dimensions": {
                        "length": 5.5,
                        "width": 3.5,
                        "unit": "meters"
                    },
                    "currentOccupant": None,
                    "sensorId": None,
                    "createdAt": zone["createdAt"],
                    "updatedAt": None
                })
                spot_counter += 1

            # Create electric spots
            for i in range(reserved.get("electric", 0)):
                parking_spots.append({
                    "spotId": f"SPOT{spot_counter:08d}",
                    "zoneId": zone["zoneId"],
                    "spotNumber": f"EV-{i+1:02d}",
                    "type": "electric",
                    "status": random.choice(["available", "occupied", "reserved"]),
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            base_coords[0] + random.uniform(-0.0002, 0.0002),
                            base_coords[1] + random.uniform(-0.0002, 0.0002)
                        ],
                        "level": 0 if zone["type"] != "garage" else random.randint(0, 2),
                        "section": "B"
                    },
                    "dimensions": {
                        "length": 5.0,
                        "width": 2.5,
                        "unit": "meters"
                    },
                    "currentOccupant": None,
                    "sensorId": None,
                    "createdAt": zone["createdAt"],
                    "updatedAt": None
                })
                spot_counter += 1

            # Create VIP spots
            for i in range(reserved.get("vip", 0)):
                parking_spots.append({
                    "spotId": f"SPOT{spot_counter:08d}",
                    "zoneId": zone["zoneId"],
                    "spotNumber": f"VIP-{i+1:02d}",
                    "type": "vip",
                    "status": random.choice(["available", "occupied", "reserved"]),
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            base_coords[0] + random.uniform(-0.0001, 0.0001),
                            base_coords[1] + random.uniform(-0.0001, 0.0001)
                        ],
                        "level": 0 if zone["type"] != "garage" else 0,
                        "section": "VIP"
                    },
                    "dimensions": {
                        "length": 6.0,
                        "width": 3.0,
                        "unit": "meters"
                    },
                    "currentOccupant": None,
                    "sensorId": None,
                    "createdAt": zone["createdAt"],
                    "updatedAt": None
                })
                spot_counter += 1

            # Create regular spots
            sections = ["A", "B", "C", "D", "E", "F"]
            for i in range(regular_spots):
                section = random.choice(sections[:3])
                spot_type = "standard" if random.random() > 0.15 else "compact"

                # 70% occupied, 20% available, 10% other statuses
                status_weights = [0.2, 0.7, 0.05, 0.03, 0.02]
                status_choices = ["available", "occupied", "reserved", "maintenance", "violation"]
                status = random.choices(status_choices, weights=status_weights)[0]

                # Add current occupant if occupied
                current_occupant = None
                if status == "occupied":
                    entry_time = datetime.now() - timedelta(
                        minutes=random.randint(5, 180)
                    )
                    current_occupant = {
                        "vehicleId": f"VEH{random.randint(1000, 9999)}",
                        "licensePlate": f"{random.choice(['CA', 'NV', 'OR'])}-{random.randint(100, 999)}{random.choice(['ABC', 'XYZ', 'DEF'])}",
                        "entryTime": entry_time,
                        "paymentMethod": random.choice(["app", "meter", "permit"]),
                        "paidUntil": entry_time + timedelta(hours=random.randint(1, 4))
                    }

                parking_spots.append({
                    "spotId": f"SPOT{spot_counter:08d}",
                    "zoneId": zone["zoneId"],
                    "spotNumber": f"{section}-{i+1:03d}",
                    "type": spot_type,
                    "status": status,
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            base_coords[0] + random.uniform(-0.0005, 0.0005),
                            base_coords[1] + random.uniform(-0.0005, 0.0005)
                        ],
                        "level": 0 if zone["type"] not in ["garage", "underground"] else random.randint(-2, 5),
                        "section": section
                    },
                    "dimensions": {
                        "length": 5.0 if spot_type == "standard" else 4.5,
                        "width": 2.5 if spot_type == "standard" else 2.2,
                        "unit": "meters"
                    },
                    "currentOccupant": current_occupant,
                    "sensorId": None,
                    "createdAt": zone["createdAt"],
                    "updatedAt": datetime.now() if status != "available" else None
                })
                spot_counter += 1

        # Insert parking spots
        if parking_spots:
            result = self.db.parking_spots.insert_many(parking_spots)
            print(f"Seeded {len(result.inserted_ids)} parking spots")

        return parking_spots

    def seed_sensors(self, parking_spots):
        """Seed sensors for parking spots."""
        sensors = []
        sensor_counter = 1

        # Sensor deployment rate by spot type
        sensor_rates = {
            "standard": 0.7,
            "compact": 0.7,
            "disabled": 0.9,
            "electric": 0.95,
            "vip": 1.0,
            "loading": 0.8,
            "motorcycle": 0.5
        }

        for spot in parking_spots:
            # Determine if this spot gets a sensor
            deploy_rate = sensor_rates.get(spot["type"], 0.7)
            if random.random() < deploy_rate:
                # Choose sensor type based on location
                if spot["location"].get("level", 0) != 0:
                    # Underground/multilevel - use ultrasonic or infrared
                    sensor_type = random.choice(["ultrasonic", "infrared", "magnetometer"])
                else:
                    # Street level - prefer magnetometer
                    sensor_type = random.choices(
                        ["magnetometer", "ultrasonic", "infrared", "camera"],
                        weights=[0.6, 0.2, 0.15, 0.05]
                    )[0]

                # Sensor status
                status_weights = [0.85, 0.05, 0.05, 0.03, 0.02]
                status_choices = ["active", "inactive", "faulty", "maintenance", "offline"]
                sensor_status = random.choices(status_choices, weights=status_weights)[0]

                sensor = {
                    "sensorId": f"SEN{sensor_counter:08d}",
                    "type": sensor_type,
                    "model": {
                        "magnetometer": "ParkSense MAG-3000",
                        "ultrasonic": "UltraPark US-200",
                        "infrared": "IRDetect Pro",
                        "camera": "SmartEye CV-500",
                        "radar": "RadarPark RP-100"
                    }.get(sensor_type, "Generic Sensor"),
                    "spotId": spot["spotId"],
                    "zoneId": spot["zoneId"],
                    "status": sensor_status,
                    "connectivity": {
                        "protocol": random.choice(["LoRa", "NB-IoT", "WiFi"]) if sensor_type != "camera" else "4G",
                        "gatewayId": f"GW{spot['zoneId'][-4:]}",
                        "signalStrength": random.randint(-80, -40),
                        "lastSeen": datetime.now() - timedelta(minutes=random.randint(0, 60))
                    },
                    "calibration": {
                        "baseline": random.uniform(100, 200) if sensor_type == "magnetometer" else random.uniform(0, 10),
                        "threshold": random.uniform(50, 100) if sensor_type == "magnetometer" else random.uniform(5, 15),
                        "sensitivity": random.randint(5, 8),
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 180))
                    },
                    "batteryLevel": random.randint(60, 100) if sensor_type != "camera" else None,
                    "firmware": {
                        "version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
                        "lastUpdate": datetime.now() - timedelta(days=random.randint(7, 90))
                    },
                    "installedAt": spot["createdAt"] + timedelta(days=random.randint(0, 30)),
                    "lastReading": datetime.now() - timedelta(minutes=random.randint(0, 10))
                }

                sensors.append(sensor)

                # Update spot with sensor ID
                spot["sensorId"] = sensor["sensorId"]
                self.db.parking_spots.update_one(
                    {"spotId": spot["spotId"]},
                    {"$set": {"sensorId": sensor["sensorId"]}}
                )

                sensor_counter += 1

        # Insert sensors
        if sensors:
            result = self.db.sensors.insert_many(sensors)
            print(f"Seeded {len(result.inserted_ids)} sensors")

        return sensors

    def seed_initial_events(self, parking_spots):
        """Seed some initial events."""
        events = []
        event_counter = 1

        # Recent occupancy changes
        for spot in random.sample([s for s in parking_spots if s.get("sensorId")],
                                 min(50, len([s for s in parking_spots if s.get("sensorId")]))):

            for _ in range(random.randint(1, 3)):
                event_time = datetime.now() - timedelta(
                    hours=random.randint(1, 48),
                    minutes=random.randint(0, 59)
                )

                event_type = random.choice([
                    "occupancy_change",
                    "overstay_warning",
                    "payment_expired",
                    "sensor_offline"
                ])

                events.append({
                    "eventId": f"EVT{event_counter:010d}",
                    "eventType": event_type,
                    "spotId": spot["spotId"],
                    "zoneId": spot["zoneId"],
                    "sensorId": spot.get("sensorId"),
                    "timestamp": event_time,
                    "endTime": event_time + timedelta(minutes=random.randint(1, 30)) if event_type == "sensor_offline" else None,
                    "details": {
                        "previousStatus": "available" if event_type == "occupancy_change" else None,
                        "newStatus": "occupied" if event_type == "occupancy_change" else None,
                        "confidence": random.uniform(0.85, 0.99) if event_type == "occupancy_change" else None,
                        "vehicleId": f"VEH{random.randint(1000, 9999)}" if event_type in ["occupancy_change", "overstay_warning"] else None,
                        "duration": random.randint(60, 240) if event_type == "overstay_warning" else None
                    },
                    "severity": "info" if event_type == "occupancy_change" else "warning",
                    "acknowledged": random.choice([True, False]),
                    "acknowledgedBy": "system" if random.random() > 0.5 else None,
                    "acknowledgedAt": event_time + timedelta(minutes=random.randint(5, 60)) if random.random() > 0.5 else None
                })
                event_counter += 1

        # Insert events
        if events:
            result = self.db.events.insert_many(events)
            print(f"Seeded {len(result.inserted_ids)} initial events")

        return events

    def seed_initial_violations(self, parking_spots):
        """Seed some initial violations."""
        violations = []
        violation_counter = 1

        # Create violations for some occupied spots
        violated_spots = random.sample(
            [s for s in parking_spots if s["status"] in ["occupied", "violation"]],
            min(15, len([s for s in parking_spots if s["status"] in ["occupied", "violation"]]))
        )

        for spot in violated_spots:
            violation_time = datetime.now() - timedelta(
                hours=random.randint(1, 72),
                minutes=random.randint(0, 59)
            )

            violation_type = random.choice([
                "overstay",
                "no_payment",
                "invalid_permit",
                "wrong_spot_type",
                "outside_hours"
            ])

            fine_amounts = {
                "overstay": 35.00,
                "no_payment": 65.00,
                "invalid_permit": 45.00,
                "wrong_spot_type": 55.00,
                "outside_hours": 25.00
            }

            violation = {
                "violationId": f"VIO{violation_counter:010d}",
                "type": violation_type,
                "spotId": spot["spotId"],
                "zoneId": spot["zoneId"],
                "vehicle": {
                    "licensePlate": f"{random.choice(['CA', 'NV', 'OR'])}-{random.randint(100, 999)}{random.choice(['ABC', 'XYZ'])}",
                    "make": random.choice(["Toyota", "Honda", "Ford", "Tesla", "BMW"]),
                    "model": random.choice(["Camry", "Accord", "F-150", "Model 3", "X5"]),
                    "color": random.choice(["White", "Black", "Silver", "Blue", "Red"]),
                    "imageUrl": None
                },
                "timestamp": violation_time,
                "detectedBy": random.choice(["sensor", "camera", "officer"]),
                "fine": {
                    "amount": fine_amounts[violation_type],
                    "currency": "USD",
                    "dueDate": violation_time + timedelta(days=30)
                },
                "status": random.choice(["active", "paid", "disputed", "active", "active"]),
                "evidence": [
                    {
                        "type": "sensor_log",
                        "url": f"/evidence/sensor/{violation_counter}",
                        "timestamp": violation_time
                    }
                ],
                "officer": {
                    "badgeNumber": f"P{random.randint(1000, 9999)}",
                    "name": f"Officer {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}"
                } if random.random() > 0.5 else None,
                "resolution": None
            }

            if violation["status"] == "paid":
                violation["resolution"] = {
                    "status": "paid",
                    "date": violation_time + timedelta(days=random.randint(1, 20)),
                    "amount": violation["fine"]["amount"],
                    "notes": "Paid online"
                }

            violations.append(violation)
            violation_counter += 1

        # Insert violations
        if violations:
            result = self.db.violations.insert_many(violations)
            print(f"Seeded {len(result.inserted_ids)} initial violations")

        return violations

    def run(self, clean=False):
        """Run the complete seeding process."""
        print("\n" + "="*50)
        print("Smart Parking Occupancy - Infrastructure Seeding")
        print("="*50)

        if clean:
            print("\nCleaning existing data...")
            self.clean_collections()

        print("\nSeeding infrastructure data...")

        # Seed zones
        zones = self.seed_zones()

        # Seed parking spots
        parking_spots = self.seed_parking_spots(zones)

        # Seed sensors
        sensors = self.seed_sensors(parking_spots)

        # Seed initial events
        events = self.seed_initial_events(parking_spots)

        # Seed initial violations
        violations = self.seed_initial_violations(parking_spots)

        print("\n" + "="*50)
        print("Seeding complete!")
        print(f"Database: {self.db.name}")
        print(f"Zones: {len(zones)}")
        print(f"Parking spots: {len(parking_spots)}")
        print(f"Sensors: {len(sensors)}")
        print(f"Events: {len(events)}")
        print(f"Violations: {len(violations)}")
        print("="*50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed smart parking infrastructure data")
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
    seeder = SmartParkingSeeder(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    seeder.run(clean=args.clean)


if __name__ == "__main__":
    main()