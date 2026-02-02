#!/usr/bin/env python3
"""
Smart Parking Occupancy - Simulation Script
Simulates parking occupancy changes, sensor readings, and violations
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
import random
import argparse
import time
import math

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "smartparking_db"


class ParkingSimulator:
    """Simulates parking occupancy and events."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize simulator."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

        # Load infrastructure
        self.zones = list(self.db.zones.find())
        self.parking_spots = list(self.db.parking_spots.find())
        self.sensors = list(self.db.sensors.find({"status": "active"}))

        if not self.zones:
            print("No zones found. Please run seed script first.")
            sys.exit(1)

        if not self.parking_spots:
            print("No parking spots found. Please run seed script first.")
            sys.exit(1)

        if not self.sensors:
            print("No sensors found. Please run seed script first.")
            sys.exit(1)

        print(f"Loaded {len(self.zones)} zones, {len(self.parking_spots)} spots, {len(self.sensors)} sensors")

        # Build spot-sensor mapping
        self.spot_sensors = {}
        for sensor in self.sensors:
            if sensor.get("spotId"):
                self.spot_sensors[sensor["spotId"]] = sensor

        # Zone statistics cache
        self.zone_stats = {}
        for zone in self.zones:
            zone_spots = [s for s in self.parking_spots if s["zoneId"] == zone["zoneId"]]
            self.zone_stats[zone["zoneId"]] = {
                "total": len(zone_spots),
                "occupied": len([s for s in zone_spots if s["status"] == "occupied"]),
                "available": len([s for s in zone_spots if s["status"] == "available"]),
                "reserved": len([s for s in zone_spots if s["status"] == "reserved"])
            }

    def get_parking_demand(self, zone_type, hour):
        """Calculate parking demand based on zone type and time of day."""
        # Base demand patterns by zone type and hour
        patterns = {
            "street": {
                # Downtown street parking - high during business hours
                0: 0.2, 1: 0.15, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.15,
                6: 0.25, 7: 0.45, 8: 0.75, 9: 0.85, 10: 0.9, 11: 0.92,
                12: 0.88, 13: 0.9, 14: 0.92, 15: 0.9, 16: 0.88, 17: 0.85,
                18: 0.7, 19: 0.6, 20: 0.5, 21: 0.4, 22: 0.3, 23: 0.25
            },
            "garage": {
                # Parking garage - steady during business hours
                0: 0.1, 1: 0.08, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.08,
                6: 0.2, 7: 0.4, 8: 0.6, 9: 0.75, 10: 0.8, 11: 0.82,
                12: 0.8, 13: 0.82, 14: 0.85, 15: 0.83, 16: 0.8, 17: 0.75,
                18: 0.6, 19: 0.45, 20: 0.35, 21: 0.25, 22: 0.18, 23: 0.12
            },
            "lot": {
                # Shopping/retail lot - peaks midday and evening
                0: 0.05, 1: 0.03, 2: 0.02, 3: 0.02, 4: 0.02, 5: 0.03,
                6: 0.08, 7: 0.15, 8: 0.25, 9: 0.4, 10: 0.6, 11: 0.75,
                12: 0.85, 13: 0.82, 14: 0.78, 15: 0.75, 16: 0.72, 17: 0.7,
                18: 0.8, 19: 0.85, 20: 0.7, 21: 0.5, 22: 0.3, 23: 0.15
            }
        }

        # Default pattern for other types
        default_pattern = patterns.get("lot")

        # Get base demand
        base_demand = patterns.get(zone_type, default_pattern).get(hour, 0.5)

        # Add some randomness
        demand = base_demand + random.gauss(0, 0.05)

        # Add day-of-week variation
        day_of_week = datetime.now().weekday()
        if day_of_week in [5, 6]:  # Weekend
            if zone_type == "street":
                demand *= 0.7  # Less business district parking
            elif zone_type == "lot":
                demand *= 1.2  # More shopping

        # Clamp between 0 and 1
        return max(0.05, min(0.95, demand))

    def simulate_occupancy_change(self, spot, sensor, confidence=None):
        """Simulate an occupancy change for a parking spot."""
        # Determine new status based on current status
        current_status = spot["status"]

        if current_status == "available":
            # Spot can become occupied or reserved
            new_status = random.choices(
                ["occupied", "reserved", "available"],
                weights=[0.7, 0.2, 0.1]
            )[0]
        elif current_status == "occupied":
            # Spot can become available or violation
            new_status = random.choices(
                ["available", "occupied", "violation"],
                weights=[0.4, 0.5, 0.1]
            )[0]
        elif current_status == "reserved":
            # Reserved spot usually becomes occupied
            new_status = random.choices(
                ["occupied", "available", "reserved"],
                weights=[0.7, 0.2, 0.1]
            )[0]
        else:
            # Maintenance or violation - less likely to change
            new_status = random.choices(
                ["available", current_status],
                weights=[0.3, 0.7]
            )[0]

        # Generate confidence score if not provided
        if confidence is None:
            if sensor["type"] == "magnetometer":
                confidence = random.uniform(0.92, 0.99)
            elif sensor["type"] == "ultrasonic":
                confidence = random.uniform(0.88, 0.96)
            elif sensor["type"] == "infrared":
                confidence = random.uniform(0.85, 0.94)
            elif sensor["type"] == "camera":
                confidence = random.uniform(0.95, 0.99)
            else:
                confidence = random.uniform(0.80, 0.90)

        return new_status, confidence

    def generate_occupancy_reading(self, spot, sensor, timestamp, status=None, confidence=None):
        """Generate an occupancy reading."""
        if status is None:
            status = spot["status"]

        if confidence is None:
            confidence = random.uniform(0.85, 0.99)

        # Sensor-specific readings
        sensor_data = {}
        if sensor["type"] == "magnetometer":
            # Magnetic field readings
            baseline = sensor.get("calibration", {}).get("baseline", 150)
            if status == "occupied":
                sensor_data["magneticField"] = baseline + random.uniform(50, 200)
            else:
                sensor_data["magneticField"] = baseline + random.uniform(-10, 10)
            sensor_data["fieldStrength"] = abs(sensor_data["magneticField"] - baseline)

        elif sensor["type"] == "ultrasonic":
            # Distance readings in cm
            if status == "occupied":
                sensor_data["distance"] = random.uniform(50, 150)  # Vehicle present
            else:
                sensor_data["distance"] = random.uniform(200, 400)  # No vehicle
            sensor_data["echoTime"] = sensor_data["distance"] / 343.0 * 2000  # microseconds

        elif sensor["type"] == "infrared":
            # IR sensor readings
            if status == "occupied":
                sensor_data["irReflection"] = random.uniform(0.7, 0.95)
            else:
                sensor_data["irReflection"] = random.uniform(0.1, 0.3)
            sensor_data["temperature"] = random.uniform(15, 35)  # Ambient temperature

        reading = {
            "timestamp": timestamp,
            "meta": {
                "spotId": spot["spotId"],
                "sensorId": sensor["sensorId"],
                "zoneId": spot["zoneId"]
            },
            "occupied": status == "occupied",
            "confidence": round(confidence, 3),
            "status": status,
            **sensor_data,
            "batteryLevel": sensor.get("batteryLevel", random.randint(70, 100)),
            "signalStrength": random.randint(-80, -40),
            "processingTime": random.uniform(10, 50)  # milliseconds
        }

        return reading

    def generate_event(self, spot, event_type, timestamp, details=None):
        """Generate a parking event."""
        event_counter = int(timestamp.timestamp() * 1000)

        severity_map = {
            "occupancy_change": "info",
            "overstay_warning": "warning",
            "overstay_violation": "critical",
            "payment_expired": "warning",
            "sensor_offline": "warning",
            "sensor_fault": "critical",
            "illegal_parking": "critical",
            "reservation_start": "info",
            "reservation_end": "info"
        }

        event = {
            "eventId": f"EVT{event_counter % 10000000000:010d}",
            "eventType": event_type,
            "spotId": spot["spotId"],
            "zoneId": spot["zoneId"],
            "sensorId": spot.get("sensorId"),
            "timestamp": timestamp,
            "endTime": None,
            "details": details or {},
            "severity": severity_map.get(event_type, "info"),
            "acknowledged": False,
            "acknowledgedBy": None,
            "acknowledgedAt": None
        }

        return event

    def generate_violation(self, spot, violation_type, timestamp):
        """Generate a parking violation."""
        violation_counter = int(timestamp.timestamp() * 1000)

        fine_amounts = {
            "overstay": 35.00,
            "no_payment": 65.00,
            "invalid_permit": 45.00,
            "wrong_spot_type": 55.00,
            "outside_hours": 25.00,
            "double_parking": 100.00,
            "blocked_access": 150.00
        }

        # Generate vehicle info
        license_plates = ["CA", "NV", "OR", "WA", "AZ"]
        makes = ["Toyota", "Honda", "Ford", "Tesla", "BMW", "Audi", "Mercedes"]
        models = ["Camry", "Accord", "F-150", "Model 3", "X5", "A4", "C-Class"]
        colors = ["White", "Black", "Silver", "Blue", "Red", "Gray", "Green"]

        violation = {
            "violationId": f"VIO{violation_counter % 10000000000:010d}",
            "type": violation_type,
            "spotId": spot["spotId"],
            "zoneId": spot["zoneId"],
            "vehicle": {
                "licensePlate": f"{random.choice(license_plates)}-{random.randint(100, 999)}{random.choice(['ABC', 'XYZ', 'DEF', 'GHI'])}",
                "make": random.choice(makes),
                "model": random.choice(models),
                "color": random.choice(colors),
                "imageUrl": f"/images/violations/{violation_counter}.jpg" if random.random() > 0.5 else None
            },
            "timestamp": timestamp,
            "detectedBy": "sensor" if spot.get("sensorId") else random.choice(["camera", "officer"]),
            "fine": {
                "amount": fine_amounts.get(violation_type, 50.00),
                "currency": "USD",
                "dueDate": timestamp + timedelta(days=30)
            },
            "status": "active",
            "evidence": [
                {
                    "type": "sensor_log",
                    "url": f"/evidence/sensor/{violation_counter}",
                    "timestamp": timestamp
                }
            ],
            "officer": None,
            "resolution": None
        }

        return violation

    def update_zone_stats(self, zone_id, change_type):
        """Update zone statistics cache."""
        if zone_id in self.zone_stats:
            if change_type == "occupy":
                self.zone_stats[zone_id]["occupied"] += 1
                self.zone_stats[zone_id]["available"] -= 1
            elif change_type == "vacate":
                self.zone_stats[zone_id]["occupied"] -= 1
                self.zone_stats[zone_id]["available"] += 1

    def simulate_time_step(self, current_time):
        """Simulate one time step."""
        readings = []
        events = []
        violations = []

        hour = current_time.hour
        minute = current_time.minute

        # Process each zone
        for zone in self.zones:
            zone_type = zone["type"]
            zone_id = zone["zoneId"]

            # Get demand for this zone
            demand = self.get_parking_demand(zone_type, hour)

            # Get spots in this zone with sensors
            zone_spots = [s for s in self.parking_spots
                         if s["zoneId"] == zone_id and s.get("sensorId")]

            if not zone_spots:
                continue

            # Calculate target occupancy
            target_occupied = int(len(zone_spots) * demand)
            current_occupied = len([s for s in zone_spots if s["status"] == "occupied"])

            # Determine how many changes to make
            changes_needed = abs(target_occupied - current_occupied)
            changes_to_make = min(changes_needed, max(1, int(len(zone_spots) * 0.1)))  # Max 10% change per step

            # Make occupancy changes
            if current_occupied < target_occupied:
                # Need to fill spots
                available_spots = [s for s in zone_spots if s["status"] == "available"]
                spots_to_fill = random.sample(available_spots, min(changes_to_make, len(available_spots)))

                for spot in spots_to_fill:
                    sensor = self.spot_sensors.get(spot["spotId"])
                    if sensor and sensor["status"] == "active":
                        new_status, confidence = self.simulate_occupancy_change(spot, sensor)

                        if new_status == "occupied":
                            # Generate occupancy reading
                            reading = self.generate_occupancy_reading(
                                spot, sensor, current_time, new_status, confidence
                            )
                            readings.append(reading)

                            # Generate occupancy change event
                            event = self.generate_event(
                                spot, "occupancy_change", current_time,
                                {
                                    "previousStatus": "available",
                                    "newStatus": "occupied",
                                    "confidence": confidence,
                                    "vehicleId": f"VEH{random.randint(10000, 99999)}",
                                    "duration": None
                                }
                            )
                            events.append(event)

                            # Update spot status
                            spot["status"] = "occupied"
                            spot["currentOccupant"] = {
                                "vehicleId": event["details"]["vehicleId"],
                                "licensePlate": f"CA-{random.randint(100, 999)}ABC",
                                "entryTime": current_time,
                                "paymentMethod": random.choice(["app", "meter", "permit"]),
                                "paidUntil": current_time + timedelta(hours=random.randint(1, 4))
                            }
                            self.update_zone_stats(zone_id, "occupy")

            elif current_occupied > target_occupied:
                # Need to vacate spots
                occupied_spots = [s for s in zone_spots if s["status"] == "occupied"]
                spots_to_vacate = random.sample(occupied_spots, min(changes_to_make, len(occupied_spots)))

                for spot in spots_to_vacate:
                    sensor = self.spot_sensors.get(spot["spotId"])
                    if sensor and sensor["status"] == "active":
                        # Check for overstay before leaving
                        if spot.get("currentOccupant") and spot["currentOccupant"].get("paidUntil"):
                            if current_time > spot["currentOccupant"]["paidUntil"]:
                                # Generate overstay violation
                                overstay_duration = (current_time - spot["currentOccupant"]["paidUntil"]).total_seconds() / 60
                                if overstay_duration > 15:  # 15 minutes grace period
                                    violation = self.generate_violation(spot, "overstay", current_time)
                                    violations.append(violation)

                                    event = self.generate_event(
                                        spot, "overstay_violation", current_time,
                                        {
                                            "overstayMinutes": int(overstay_duration),
                                            "vehicleId": spot["currentOccupant"].get("vehicleId"),
                                            "fineAmount": violation["fine"]["amount"]
                                        }
                                    )
                                    events.append(event)

                        # Generate vacancy reading
                        reading = self.generate_occupancy_reading(
                            spot, sensor, current_time, "available", random.uniform(0.90, 0.99)
                        )
                        readings.append(reading)

                        # Generate occupancy change event
                        duration = None
                        if spot.get("currentOccupant") and spot["currentOccupant"].get("entryTime"):
                            duration = int((current_time - spot["currentOccupant"]["entryTime"]).total_seconds() / 60)

                        event = self.generate_event(
                            spot, "occupancy_change", current_time,
                            {
                                "previousStatus": "occupied",
                                "newStatus": "available",
                                "confidence": reading["confidence"],
                                "vehicleId": spot.get("currentOccupant", {}).get("vehicleId"),
                                "duration": duration
                            }
                        )
                        events.append(event)

                        # Update spot status
                        spot["status"] = "available"
                        spot["currentOccupant"] = None
                        self.update_zone_stats(zone_id, "vacate")

            # Regular sensor readings for spots that didn't change
            for spot in zone_spots:
                if random.random() < 0.1:  # 10% chance of regular reading
                    sensor = self.spot_sensors.get(spot["spotId"])
                    if sensor and sensor["status"] == "active":
                        reading = self.generate_occupancy_reading(
                            spot, sensor, current_time, spot["status"]
                        )
                        readings.append(reading)

            # Check for payment expirations
            if minute == 0:  # Check every hour
                for spot in zone_spots:
                    if spot["status"] == "occupied" and spot.get("currentOccupant"):
                        occupant = spot["currentOccupant"]
                        if occupant.get("paidUntil") and current_time > occupant["paidUntil"]:
                            event = self.generate_event(
                                spot, "payment_expired", current_time,
                                {
                                    "vehicleId": occupant.get("vehicleId"),
                                    "expiredAt": occupant["paidUntil"],
                                    "minutesOverdue": int((current_time - occupant["paidUntil"]).total_seconds() / 60)
                                }
                            )
                            events.append(event)

            # Simulate sensor issues (rare)
            if random.random() < 0.001:  # 0.1% chance per zone per step
                faulty_sensor = random.choice([s for s in self.sensors if s["zoneId"] == zone_id])
                spot = next((s for s in zone_spots if s.get("sensorId") == faulty_sensor["sensorId"]), None)
                if spot:
                    event = self.generate_event(
                        spot, "sensor_offline", current_time,
                        {
                            "sensorId": faulty_sensor["sensorId"],
                            "lastSeen": current_time,
                            "batteryLevel": faulty_sensor.get("batteryLevel", 0)
                        }
                    )
                    events.append(event)

        return readings, events, violations

    def run_simulation(self, duration_hours=1, step_minutes=5):
        """Run the simulation for specified duration."""
        print(f"\nStarting parking simulation for {duration_hours} hours...")
        print(f"Step interval: {step_minutes} minutes")

        start_time = datetime.now()
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)

        total_readings = 0
        total_events = 0
        total_violations = 0

        batch_size = 1000
        reading_batch = []
        event_batch = []
        violation_batch = []

        step_count = 0
        total_steps = int(duration_hours * 60 / step_minutes)

        while current_time < end_time:
            # Simulate time step
            readings, events, violations = self.simulate_time_step(current_time)

            reading_batch.extend(readings)
            event_batch.extend(events)
            violation_batch.extend(violations)

            # Insert in batches
            if len(reading_batch) >= batch_size:
                self.db.occupancy_readings.insert_many(reading_batch)
                total_readings += len(reading_batch)
                reading_batch = []

            if event_batch:
                self.db.events.insert_many(event_batch)
                total_events += len(event_batch)
                event_batch = []

            if violation_batch:
                self.db.violations.insert_many(violation_batch)
                total_violations += len(violation_batch)
                violation_batch = []

            # Progress update
            step_count += 1
            if step_count % 10 == 0:
                progress = (step_count / total_steps) * 100
                print(f"Progress: {progress:.1f}% - Readings: {total_readings}, "
                      f"Events: {total_events}, Violations: {total_violations}")

            # Show zone statistics periodically
            if step_count % 20 == 0:
                for zone_id, stats in self.zone_stats.items():
                    occupancy_rate = stats["occupied"] / stats["total"] * 100 if stats["total"] > 0 else 0
                    print(f"  Zone {zone_id}: {occupancy_rate:.1f}% occupied "
                          f"({stats['occupied']}/{stats['total']} spots)")

            # Advance time
            current_time += timedelta(minutes=step_minutes)

        # Insert remaining batches
        if reading_batch:
            self.db.occupancy_readings.insert_many(reading_batch)
            total_readings += len(reading_batch)

        if event_batch:
            self.db.events.insert_many(event_batch)
            total_events += len(event_batch)

        if violation_batch:
            self.db.violations.insert_many(violation_batch)
            total_violations += len(violation_batch)

        # Summary
        print("\n" + "="*50)
        print("Simulation Complete!")
        print(f"Duration: {duration_hours} hours")
        print(f"Occupancy readings generated: {total_readings}")
        print(f"Events generated: {total_events}")
        print(f"Violations generated: {total_violations}")
        print(f"Average readings/hour: {total_readings/duration_hours:.1f}")

        # Final zone statistics
        print("\nFinal Zone Occupancy Rates:")
        for zone in self.zones:
            zone_id = zone["zoneId"]
            if zone_id in self.zone_stats:
                stats = self.zone_stats[zone_id]
                occupancy_rate = stats["occupied"] / stats["total"] * 100 if stats["total"] > 0 else 0
                print(f"  {zone['name']}: {occupancy_rate:.1f}% "
                      f"({stats['occupied']}/{stats['total']} spots)")

        print("="*50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simulate smart parking occupancy")
    parser.add_argument("--hours", type=float, default=1,
                      help="Duration of simulation in hours")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--step-minutes", type=int, default=5,
                      help="Time step in minutes")
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

    # Run simulator
    simulator = ParkingSimulator(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    simulator.run_simulation(
        duration_hours=args.hours,
        step_minutes=args.step_minutes
    )


if __name__ == "__main__":
    main()