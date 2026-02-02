#!/usr/bin/env python3
"""
Smart Grid Energy Monitoring - Consumption Simulation Script
Simulates energy consumption, power quality, and grid events
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
DB_NAME = "energygrid_db"


class EnergyConsumptionSimulator:
    """Simulates energy consumption and grid events."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize simulator."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

        # Load infrastructure
        self.buildings = list(self.db.buildings.find({"status": "active"}))
        self.meters = list(self.db.meters.find({"status": "active"}))
        self.tariffs = list(self.db.tariffs.find())

        if not self.buildings:
            print("No buildings found. Please run seed script first.")
            sys.exit(1)

        if not self.meters:
            print("No meters found. Please run seed script first.")
            sys.exit(1)

        print(f"Loaded {len(self.buildings)} buildings, {len(self.meters)} meters")

        # Build meter-building mapping
        self.building_meters = {}
        for meter in self.meters:
            building_id = meter["buildingId"]
            if building_id not in self.building_meters:
                self.building_meters[building_id] = []
            self.building_meters[building_id].append(meter)

        # Grid state
        self.grid_state = {
            "voltage": 240.0,
            "frequency": 60.0,
            "total_demand_kw": 0,
            "grid_stable": True
        }

    def get_consumption_pattern(self, building, hour, day_of_week):
        """Get consumption pattern based on building type and time."""
        # Base patterns by building type
        patterns = {
            "residential": {
                # Higher morning and evening peaks
                0: 0.3, 1: 0.25, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.25,
                6: 0.4, 7: 0.6, 8: 0.7, 9: 0.5, 10: 0.4, 11: 0.4,
                12: 0.45, 13: 0.45, 14: 0.4, 15: 0.45, 16: 0.5, 17: 0.65,
                18: 0.8, 19: 0.9, 20: 0.85, 21: 0.7, 22: 0.5, 23: 0.4
            },
            "commercial": {
                # Business hours peak
                0: 0.2, 1: 0.15, 2: 0.15, 3: 0.15, 4: 0.15, 5: 0.2,
                6: 0.3, 7: 0.5, 8: 0.7, 9: 0.85, 10: 0.9, 11: 0.92,
                12: 0.88, 13: 0.9, 14: 0.92, 15: 0.9, 16: 0.88, 17: 0.75,
                18: 0.6, 19: 0.4, 20: 0.3, 21: 0.25, 22: 0.22, 23: 0.2
            },
            "industrial": {
                # 24/7 with shift patterns
                0: 0.7, 1: 0.65, 2: 0.65, 3: 0.65, 4: 0.65, 5: 0.7,
                6: 0.75, 7: 0.85, 8: 0.9, 9: 0.92, 10: 0.92, 11: 0.92,
                12: 0.88, 13: 0.9, 14: 0.92, 15: 0.9, 16: 0.85, 17: 0.8,
                18: 0.75, 19: 0.75, 20: 0.75, 21: 0.75, 22: 0.72, 23: 0.7
            }
        }

        # Get base pattern
        base_pattern = patterns.get(building["type"], patterns["residential"])
        base_load = base_pattern[hour]

        # Adjust for specific building subtypes
        subtype_adjustments = {
            "single_family": 1.0,
            "apartment": 0.9,
            "condo": 0.95,
            "office": 1.0,
            "retail": 1.1,
            "hospital": 1.2,  # Always high
            "school": 0.8 if day_of_week < 5 else 0.3,  # Lower on weekends
            "factory": 1.0 if day_of_week < 5 else 0.7,
            "warehouse": 0.9,
            "data_center": 1.0  # Constant high load
        }

        adjustment = subtype_adjustments.get(building.get("subType"), 1.0)

        # Weekend adjustment
        if day_of_week >= 5:  # Saturday/Sunday
            if building["type"] == "residential":
                base_load *= 1.1  # Slightly higher on weekends
            elif building["type"] == "commercial":
                base_load *= 0.3  # Much lower on weekends
                if building["subType"] == "retail":
                    base_load *= 2.0  # Retail busier on weekends
            elif building["type"] == "industrial":
                base_load *= 0.8  # Reduced industrial on weekends

        # Apply adjustment
        consumption_factor = base_load * adjustment

        # Add some randomness
        consumption_factor += random.gauss(0, 0.05)

        # Clamp between 0.1 and 1.0
        return max(0.1, min(1.0, consumption_factor))

    def calculate_base_load(self, building):
        """Calculate base load in kW for a building."""
        base_loads = {
            "single_family": random.uniform(1.5, 3.5),
            "apartment": random.uniform(1.0, 2.0) * building["characteristics"]["units"],
            "condo": random.uniform(1.2, 2.5) * building["characteristics"]["units"],
            "office": building["characteristics"]["squareMeters"] * 0.025,
            "retail": building["characteristics"]["squareMeters"] * 0.030,
            "hospital": building["characteristics"]["squareMeters"] * 0.040,
            "school": building["characteristics"]["squareMeters"] * 0.020,
            "factory": building["characteristics"]["squareMeters"] * 0.035,
            "warehouse": building["characteristics"]["squareMeters"] * 0.015,
            "data_center": building["characteristics"]["squareMeters"] * 0.100
        }

        return base_loads.get(building.get("subType"), 5.0)

    def generate_reading(self, meter, building, timestamp, consumption_factor):
        """Generate an energy reading for a meter."""
        # Calculate power consumption
        base_load_kw = self.calculate_base_load(building)
        current_kw = base_load_kw * consumption_factor

        # Add variation for realism
        current_kw *= random.uniform(0.95, 1.05)

        # Power factor (industrial typically lower)
        if building["type"] == "industrial":
            power_factor = random.uniform(0.80, 0.92)
        else:
            power_factor = random.uniform(0.90, 0.99)

        # Calculate electrical parameters
        voltage = self.grid_state["voltage"] + random.gauss(0, 2)
        current = (current_kw * 1000) / (voltage * power_factor)  # Amperes
        apparent_power = current_kw / power_factor  # kVA
        reactive_power = math.sqrt(apparent_power**2 - current_kw**2)  # kVAR

        # Frequency variation
        frequency = self.grid_state["frequency"] + random.gauss(0, 0.05)

        # Calculate energy consumed since last reading (assume 15-minute intervals)
        kwh_consumed = current_kw * 0.25  # 15 minutes = 0.25 hours

        # Three-phase systems have different readings
        if meter.get("subType") == "three_phase":
            phase_voltages = [voltage + random.gauss(0, 1) for _ in range(3)]
            phase_currents = [current / 3 + random.gauss(0, 0.5) for _ in range(3)]
            phase_imbalance = max(abs(c - current/3) / (current/3) for c in phase_currents) if current > 0 else 0
        else:
            phase_voltages = [voltage]
            phase_currents = [current]
            phase_imbalance = 0

        reading = {
            "timestamp": timestamp,
            "meta": {
                "meterId": meter["meterId"],
                "buildingId": building["buildingId"],
                "meterType": meter["type"],
                "readingType": "interval"  # interval|snapshot|cumulative
            },

            # Energy consumption
            "kWhConsumed": round(kwh_consumed, 3),
            "kWDemand": round(current_kw, 2),
            "peakKW": round(current_kw * random.uniform(1.0, 1.1), 2),

            # Electrical parameters
            "voltage": round(voltage, 1),
            "current": round(current, 2),
            "powerFactor": round(power_factor, 3),
            "frequency": round(frequency, 2),

            # Power components
            "activePower": round(current_kw, 2),  # kW
            "reactivePower": round(reactive_power, 2),  # kVAR
            "apparentPower": round(apparent_power, 2),  # kVA

            # Phase details (for three-phase)
            "phaseVoltages": [round(v, 1) for v in phase_voltages],
            "phaseCurrents": [round(c, 2) for c in phase_currents],
            "phaseImbalance": round(phase_imbalance, 3),

            # Quality metrics
            "thd": random.uniform(0.01, 0.05),  # Total harmonic distortion
            "signalQuality": random.randint(85, 100),

            # Meter status
            "batteryLevel": None,  # Grid-powered meters
            "signalStrength": meter["connectivity"]["signalStrength"] + random.randint(-5, 5),
            "temperature": random.uniform(15, 35)  # Meter temperature
        }

        # Solar generation (if applicable)
        if meter["type"] == "solar" and building["characteristics"].get("hasSolar"):
            hour = timestamp.hour
            # Solar generation pattern (peaks at noon)
            solar_factor = max(0, math.sin((hour - 6) * math.pi / 12)) if 6 <= hour <= 18 else 0
            solar_factor *= random.uniform(0.7, 1.0)  # Weather variation

            solar_capacity = building["characteristics"]["squareMeters"] * 0.001  # kW per sqm
            solar_generation = solar_capacity * solar_factor

            reading["solarGeneration"] = round(solar_generation, 2)
            reading["netMetering"] = round(kwh_consumed - solar_generation * 0.25, 3)

        return reading

    def check_for_events(self, building, meters, timestamp):
        """Check for and generate grid events."""
        events = []
        event_counter = int(timestamp.timestamp() * 1000000)

        for meter in meters:
            # Peak demand check for commercial/industrial
            if building["type"] in ["commercial", "industrial"]:
                if random.random() < 0.01:  # 1% chance per interval
                    max_demand = building["contractInfo"]["maxDemandKW"]
                    actual_demand = max_demand * random.uniform(1.05, 1.25)

                    events.append({
                        "eventId": f"EVT{event_counter % 1000000000000:012d}",
                        "eventType": "peak_demand",
                        "meterId": meter["meterId"],
                        "buildingId": building["buildingId"],
                        "timestamp": timestamp,
                        "endTime": timestamp + timedelta(minutes=random.randint(15, 60)),
                        "severity": "warning" if actual_demand < max_demand * 1.15 else "critical",
                        "details": {
                            "duration": random.randint(15, 60) * 60,
                            "peakValue": round(actual_demand, 2),
                            "thresholdExceeded": max_demand,
                            "estimatedCost": round(actual_demand * 15.0, 2)  # Demand charge
                        },
                        "location": {
                            "grid": f"Grid-{random.randint(1, 5)}",
                            "substation": f"SUB-{random.randint(100, 999)}",
                            "feeder": f"FDR-{random.randint(1, 20)}"
                        },
                        "response": {
                            "automated": True,
                            "action": "Demand response initiated",
                            "timestamp": timestamp + timedelta(minutes=random.randint(1, 5)),
                            "result": "Load reduced"
                        },
                        "acknowledged": False,
                        "acknowledgedBy": None,
                        "acknowledgedAt": None
                    })
                    event_counter += 1

            # Power quality events
            if random.random() < 0.002:  # 0.2% chance
                event_type = random.choice(["voltage_sag", "voltage_spike", "frequency_deviation"])

                events.append({
                    "eventId": f"EVT{event_counter % 1000000000000:012d}",
                    "eventType": event_type,
                    "meterId": meter["meterId"],
                    "buildingId": building["buildingId"],
                    "timestamp": timestamp,
                    "endTime": timestamp + timedelta(seconds=random.randint(1, 60)),
                    "severity": "info" if random.random() > 0.3 else "warning",
                    "details": {
                        "duration": random.randint(1, 60),
                        "affectedUnits": random.randint(1, building["characteristics"].get("units", 1)),
                        "peakValue": 220.0 if event_type == "voltage_sag" else 260.0 if event_type == "voltage_spike" else 59.5
                    },
                    "location": {
                        "grid": f"Grid-{random.randint(1, 5)}",
                        "substation": f"SUB-{random.randint(100, 999)}",
                        "feeder": f"FDR-{random.randint(1, 20)}"
                    },
                    "response": None,
                    "acknowledged": False,
                    "acknowledgedBy": None,
                    "acknowledgedAt": None
                })
                event_counter += 1

            # Meter issues (rare)
            if random.random() < 0.0001:  # 0.01% chance
                events.append({
                    "eventId": f"EVT{event_counter % 1000000000000:012d}",
                    "eventType": random.choice(["meter_tamper", "meter_failure"]),
                    "meterId": meter["meterId"],
                    "buildingId": building["buildingId"],
                    "timestamp": timestamp,
                    "endTime": None,
                    "severity": "critical",
                    "details": {
                        "duration": None,
                        "affectedUnits": 1
                    },
                    "location": None,
                    "response": {
                        "automated": False,
                        "action": "Technician dispatch requested",
                        "timestamp": timestamp + timedelta(minutes=random.randint(30, 120)),
                        "result": "Pending"
                    },
                    "acknowledged": False,
                    "acknowledgedBy": None,
                    "acknowledgedAt": None
                })
                event_counter += 1

        # Power outage simulation (very rare, affects multiple buildings)
        if random.random() < 0.0001:  # 0.01% chance
            affected_buildings = random.sample(
                self.buildings,
                min(random.randint(5, 20), len(self.buildings))
            )

            for affected_building in affected_buildings:
                events.append({
                    "eventId": f"EVT{event_counter % 1000000000000:012d}",
                    "eventType": "power_outage",
                    "meterId": None,
                    "buildingId": affected_building["buildingId"],
                    "timestamp": timestamp,
                    "endTime": timestamp + timedelta(minutes=random.randint(30, 240)),
                    "severity": "emergency",
                    "details": {
                        "duration": random.randint(30, 240) * 60,
                        "affectedUnits": affected_building["characteristics"].get("units", 1),
                        "estimatedCost": random.uniform(1000, 10000)
                    },
                    "location": {
                        "grid": f"Grid-{random.randint(1, 5)}",
                        "substation": f"SUB-{random.randint(100, 999)}",
                        "feeder": f"FDR-{random.randint(1, 20)}"
                    },
                    "response": {
                        "automated": False,
                        "action": "Crew dispatched",
                        "timestamp": timestamp + timedelta(minutes=random.randint(15, 45)),
                        "result": "In progress"
                    },
                    "acknowledged": True,
                    "acknowledgedBy": "grid_operator",
                    "acknowledgedAt": timestamp + timedelta(minutes=random.randint(1, 10))
                })
                event_counter += 1

        return events

    def update_grid_state(self, total_demand):
        """Update grid state based on total demand."""
        # Base capacity (MW)
        grid_capacity = 1000.0

        # Calculate load percentage
        load_percent = (total_demand / 1000) / grid_capacity * 100

        # Voltage regulation
        if load_percent > 90:
            self.grid_state["voltage"] = 235.0 + random.gauss(0, 3)
            self.grid_state["grid_stable"] = False
        elif load_percent > 80:
            self.grid_state["voltage"] = 238.0 + random.gauss(0, 2)
        else:
            self.grid_state["voltage"] = 240.0 + random.gauss(0, 1)

        # Frequency regulation
        if load_percent > 95:
            self.grid_state["frequency"] = 59.8 + random.gauss(0, 0.1)
        else:
            self.grid_state["frequency"] = 60.0 + random.gauss(0, 0.05)

        self.grid_state["total_demand_kw"] = total_demand

    def simulate_time_step(self, current_time):
        """Simulate one time step for all buildings."""
        readings = []
        events = []

        hour = current_time.hour
        day_of_week = current_time.weekday()
        total_demand = 0

        for building in self.buildings:
            if building["buildingId"] not in self.building_meters:
                continue

            # Get consumption pattern
            consumption_factor = self.get_consumption_pattern(building, hour, day_of_week)

            # Generate readings for each meter
            for meter in self.building_meters[building["buildingId"]]:
                if meter["status"] != "active":
                    continue

                reading = self.generate_reading(meter, building, current_time, consumption_factor)
                readings.append(reading)
                total_demand += reading["kWDemand"]

            # Check for events
            building_events = self.check_for_events(
                building,
                self.building_meters[building["buildingId"]],
                current_time
            )
            events.extend(building_events)

        # Update grid state
        self.update_grid_state(total_demand)

        return readings, events

    def run_simulation(self, duration_hours=1, interval_minutes=15):
        """Run the simulation for specified duration."""
        print(f"\nStarting energy consumption simulation for {duration_hours} hours...")
        print(f"Reading interval: {interval_minutes} minutes")

        start_time = datetime.now()
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)

        total_readings = 0
        total_events = 0

        batch_size = 1000
        reading_batch = []
        event_batch = []

        step_count = 0
        total_steps = int(duration_hours * 60 / interval_minutes)

        while current_time < end_time:
            # Simulate time step
            readings, events = self.simulate_time_step(current_time)

            reading_batch.extend(readings)
            event_batch.extend(events)

            # Insert in batches
            if len(reading_batch) >= batch_size:
                self.db.readings.insert_many(reading_batch)
                total_readings += len(reading_batch)
                reading_batch = []

            if event_batch:
                self.db.events.insert_many(event_batch)
                total_events += len(event_batch)
                event_batch = []

            # Progress update
            step_count += 1
            if step_count % 10 == 0:
                progress = (step_count / total_steps) * 100
                print(f"Progress: {progress:.1f}% - Readings: {total_readings}, "
                      f"Events: {total_events}")
                print(f"  Grid Load: {self.grid_state['total_demand_kw']:.1f} kW, "
                      f"Voltage: {self.grid_state['voltage']:.1f}V, "
                      f"Frequency: {self.grid_state['frequency']:.2f}Hz")

            # Advance time
            current_time += timedelta(minutes=interval_minutes)

        # Insert remaining batches
        if reading_batch:
            self.db.readings.insert_many(reading_batch)
            total_readings += len(reading_batch)

        if event_batch:
            self.db.events.insert_many(event_batch)
            total_events += len(event_batch)

        # Calculate statistics
        print("\n" + "="*50)
        print("Simulation Complete!")
        print(f"Duration: {duration_hours} hours")
        print(f"Energy readings generated: {total_readings}")
        print(f"Events generated: {total_events}")
        print(f"Average readings/hour: {total_readings/duration_hours:.1f}")
        print(f"Final grid load: {self.grid_state['total_demand_kw']:.1f} kW")

        # Building statistics
        print("\nEnergy Consumption by Building Type:")
        building_stats = {}
        for building in self.buildings:
            btype = building["type"]
            if btype not in building_stats:
                building_stats[btype] = {"count": 0, "total_kw": 0}
            building_stats[btype]["count"] += 1
            building_stats[btype]["total_kw"] += self.calculate_base_load(building)

        for btype, stats in building_stats.items():
            print(f"  {btype.capitalize()}: {stats['count']} buildings, "
                  f"~{stats['total_kw']:.1f} kW total capacity")

        print("="*50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simulate energy consumption")
    parser.add_argument("--hours", type=float, default=1,
                      help="Duration of simulation in hours")
    parser.add_argument("--interval", type=int, default=15,
                      help="Reading interval in minutes")
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

    # Run simulator
    simulator = EnergyConsumptionSimulator(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    simulator.run_simulation(
        duration_hours=args.hours,
        interval_minutes=args.interval
    )


if __name__ == "__main__":
    main()