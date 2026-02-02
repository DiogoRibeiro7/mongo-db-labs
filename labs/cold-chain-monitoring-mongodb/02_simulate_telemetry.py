#!/usr/bin/env python3
"""
Cold Chain Monitoring - Simulation Script
Simulates temperature readings, events, and adaptive sampling
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
DB_NAME = "coldchain_db"


class ColdChainSimulator:
    """Simulates cold chain telemetry and events."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize simulator."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

        # Load assets and sensors
        self.assets = list(self.db.assets.find())
        self.sensors = list(self.db.sensors.find({"sensorType": "temperature", "status": "active"}))

        if not self.assets:
            print("No assets found. Please run seed script first.")
            sys.exit(1)

        if not self.sensors:
            print("No sensors found. Please run seed script first.")
            sys.exit(1)

        print(f"Loaded {len(self.assets)} assets and {len(self.sensors)} sensors")

        # Simulation state
        self.asset_states = {}
        self.init_asset_states()

    def init_asset_states(self):
        """Initialize simulation state for each asset."""
        for asset in self.assets:
            self.asset_states[asset["assetId"]] = {
                "current_temp": asset["temperatureRange"]["optimal"],
                "door_open": False,
                "door_open_time": None,
                "power_on": True,
                "sampling_mode": "normal",
                "last_sample": datetime.now(),
                "trend": "stable",  # rising, falling, stable
                "humidity": random.uniform(40, 60),
                "in_excursion": False,
                "excursion_start": None
            }

    def get_sampling_interval(self, asset_id, mode):
        """Get sampling interval based on mode."""
        intervals = {
            "normal": 300,     # 5 minutes
            "rapid": 60,       # 1 minute
            "adaptive": 120,   # 2 minutes
            "alarm": 30        # 30 seconds
        }
        return intervals.get(mode, 300)

    def simulate_temperature(self, asset, state, elapsed_seconds):
        """Simulate temperature changes."""
        temp_range = asset["temperatureRange"]
        current_temp = state["current_temp"]

        # Base temperature drift
        drift = random.gauss(0, 0.02) * (elapsed_seconds / 60)

        # Door open effect
        if state["door_open"]:
            # Temperature rises when door is open
            ambient_temp = 22.0  # Room temperature
            rise_rate = 0.1 * (elapsed_seconds / 60)  # 0.1°C per minute
            drift += rise_rate * ((ambient_temp - current_temp) / 20)

        # Power failure effect
        if not state["power_on"]:
            # Temperature drifts toward ambient
            drift += 0.2 * (elapsed_seconds / 60)

        # Asset type specific behavior
        if asset["assetType"] == "truck" and asset["status"] == "in_transit":
            # More variation during transport
            drift += random.gauss(0, 0.05) * (elapsed_seconds / 60)

        # Sinusoidal daily pattern (subtle)
        hour = datetime.now().hour
        daily_variation = 0.2 * math.sin(2 * math.pi * hour / 24)
        drift += daily_variation * (elapsed_seconds / 300)

        # Apply drift
        new_temp = current_temp + drift

        # Compressor cycles (maintain temperature)
        if state["power_on"]:
            if new_temp > temp_range["max"]:
                # Cooling kicks in
                new_temp -= 0.3 * (elapsed_seconds / 60)
                state["trend"] = "falling"
            elif new_temp < temp_range["min"]:
                # Heating/less cooling
                new_temp += 0.2 * (elapsed_seconds / 60)
                state["trend"] = "rising"
            else:
                state["trend"] = "stable"

        # Clamp to reasonable bounds
        new_temp = max(temp_range["min"] - 5, min(temp_range["max"] + 10, new_temp))

        return new_temp

    def check_adaptive_sampling(self, asset, state):
        """Determine if sampling mode should change."""
        temp_range = asset["temperatureRange"]
        current_temp = state["current_temp"]

        # Temperature-based adaptive sampling
        deviation = 0
        if current_temp > temp_range["max"]:
            deviation = current_temp - temp_range["max"]
        elif current_temp < temp_range["min"]:
            deviation = temp_range["min"] - current_temp

        # Determine sampling mode
        if deviation > 2.0:
            return "alarm"
        elif deviation > 1.0:
            return "rapid"
        elif deviation > 0.5:
            return "adaptive"
        elif state["door_open"]:
            return "rapid"
        else:
            return "normal"

    def generate_measurement(self, asset, sensor, state, timestamp):
        """Generate a measurement document."""
        measurement = {
            "timestamp": timestamp,
            "meta": {
                "assetId": asset["assetId"],
                "sensorId": sensor["sensorId"]
            },
            "temperature": round(state["current_temp"], 2),
            "humidity": round(state["humidity"], 1) if random.random() > 0.3 else None,
            "doorOpen": state["door_open"],
            "batteryLevel": sensor.get("batteryLevel", random.randint(70, 100)),
            "signalStrength": random.randint(-80, -40),
            "samplingMode": state["sampling_mode"]
        }

        # Add location for mobile assets
        if asset["assetType"] in ["truck", "container"]:
            base_coords = asset["location"]["coordinates"]
            measurement["location"] = {
                "type": "Point",
                "coordinates": [
                    base_coords[0] + random.uniform(-0.01, 0.01),
                    base_coords[1] + random.uniform(-0.01, 0.01)
                ]
            }

        return measurement

    def generate_events(self, asset, state, timestamp):
        """Generate events based on state changes."""
        events = []
        event_counter = int(timestamp.timestamp() * 1000)

        # Door events
        if not state["door_open"] and random.random() < 0.05:  # 5% chance to open door
            state["door_open"] = True
            state["door_open_time"] = timestamp
            events.append({
                "eventId": f"EVT{event_counter:010d}",
                "assetId": asset["assetId"],
                "eventType": "door_open",
                "timestamp": timestamp,
                "severity": "info",
                "details": {
                    "temperature_at_open": state["current_temp"]
                },
                "acknowledged": False
            })

        elif state["door_open"] and random.random() < 0.3:  # 30% chance to close door
            duration = (timestamp - state["door_open_time"]).total_seconds()
            events.append({
                "eventId": f"EVT{event_counter + 1:010d}",
                "assetId": asset["assetId"],
                "eventType": "door_close",
                "timestamp": timestamp,
                "endTime": timestamp,
                "severity": "info" if duration < 300 else "warning",
                "details": {
                    "duration_seconds": duration,
                    "temperature_at_close": state["current_temp"]
                },
                "acknowledged": False
            })
            state["door_open"] = False
            state["door_open_time"] = None

        # Temperature excursion events
        temp_range = asset["temperatureRange"]
        if not state["in_excursion"]:
            if state["current_temp"] > temp_range["max"] + 1 or \
               state["current_temp"] < temp_range["min"] - 1:
                state["in_excursion"] = True
                state["excursion_start"] = timestamp
                events.append({
                    "eventId": f"EVT{event_counter + 2:010d}",
                    "assetId": asset["assetId"],
                    "eventType": "temperature_excursion",
                    "timestamp": timestamp,
                    "severity": "critical" if abs(state["current_temp"] - temp_range["optimal"]) > 5 else "warning",
                    "details": {
                        "temperature": state["current_temp"],
                        "threshold": temp_range["max"] if state["current_temp"] > temp_range["optimal"] else temp_range["min"],
                        "deviation": abs(state["current_temp"] - temp_range["optimal"])
                    },
                    "acknowledged": False
                })

        return events

    def generate_alerts(self, asset, state, timestamp):
        """Generate alerts based on conditions."""
        alerts = []
        alert_counter = int(timestamp.timestamp() * 1000)
        temp_range = asset["temperatureRange"]

        # Temperature alerts
        if state["current_temp"] > temp_range["max"] + 2:
            alerts.append({
                "alertId": f"ALT{alert_counter:010d}",
                "assetId": asset["assetId"],
                "alertType": "temperature_high",
                "severity": "high" if state["current_temp"] > temp_range["max"] + 5 else "medium",
                "status": "active",
                "threshold": {
                    "metric": "temperature",
                    "operator": ">",
                    "value": temp_range["max"],
                    "duration": 300
                },
                "actualValue": state["current_temp"],
                "message": f"High temperature alert: {state['current_temp']:.1f}°C exceeds maximum {temp_range['max']}°C",
                "triggeredAt": timestamp
            })

        elif state["current_temp"] < temp_range["min"] - 2:
            alerts.append({
                "alertId": f"ALT{alert_counter + 1:010d}",
                "assetId": asset["assetId"],
                "alertType": "temperature_low",
                "severity": "high" if state["current_temp"] < temp_range["min"] - 5 else "medium",
                "status": "active",
                "threshold": {
                    "metric": "temperature",
                    "operator": "<",
                    "value": temp_range["min"],
                    "duration": 300
                },
                "actualValue": state["current_temp"],
                "message": f"Low temperature alert: {state['current_temp']:.1f}°C below minimum {temp_range['min']}°C",
                "triggeredAt": timestamp
            })

        # Door open too long alert
        if state["door_open"] and state["door_open_time"]:
            duration = (timestamp - state["door_open_time"]).total_seconds()
            if duration > 600:  # 10 minutes
                alerts.append({
                    "alertId": f"ALT{alert_counter + 2:010d}",
                    "assetId": asset["assetId"],
                    "alertType": "door_open_too_long",
                    "severity": "medium",
                    "status": "active",
                    "threshold": {
                        "metric": "door_open_duration",
                        "operator": ">",
                        "value": 600,
                        "duration": 0
                    },
                    "actualValue": duration,
                    "message": f"Door has been open for {duration/60:.1f} minutes",
                    "triggeredAt": timestamp
                })

        return alerts

    def simulate_time_step(self, current_time):
        """Simulate one time step for all assets."""
        measurements = []
        events = []
        alerts = []

        for asset in self.assets:
            asset_id = asset["assetId"]
            state = self.asset_states[asset_id]

            # Get sensors for this asset
            asset_sensors = [s for s in self.sensors if s["assetId"] == asset_id]

            if not asset_sensors:
                continue

            # Check if it's time to sample
            elapsed = (current_time - state["last_sample"]).total_seconds()
            interval = self.get_sampling_interval(asset_id, state["sampling_mode"])

            if elapsed >= interval:
                # Update temperature
                state["current_temp"] = self.simulate_temperature(asset, state, elapsed)

                # Update humidity
                state["humidity"] += random.gauss(0, 0.5)
                state["humidity"] = max(20, min(80, state["humidity"]))

                # Check adaptive sampling
                new_mode = self.check_adaptive_sampling(asset, state)
                if new_mode != state["sampling_mode"]:
                    print(f"Asset {asset['name']}: Sampling mode changed from {state['sampling_mode']} to {new_mode}")
                    state["sampling_mode"] = new_mode

                # Generate measurements for each sensor
                for sensor in asset_sensors[:1]:  # Primary sensor only for now
                    measurement = self.generate_measurement(asset, sensor, state, current_time)
                    measurements.append(measurement)

                # Generate events
                asset_events = self.generate_events(asset, state, current_time)
                events.extend(asset_events)

                # Generate alerts (less frequently)
                if random.random() < 0.1:  # 10% chance
                    asset_alerts = self.generate_alerts(asset, state, current_time)
                    alerts.extend(asset_alerts)

                state["last_sample"] = current_time

        return measurements, events, alerts

    def run_simulation(self, duration_hours=1, base_step_sec=60):
        """Run the simulation for specified duration."""
        print(f"\nStarting simulation for {duration_hours} hours...")
        print(f"Base step: {base_step_sec} seconds")

        start_time = datetime.now()
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)

        total_measurements = 0
        total_events = 0
        total_alerts = 0

        batch_size = 1000
        measurement_batch = []
        event_batch = []
        alert_batch = []

        step_count = 0
        total_steps = int(duration_hours * 3600 / base_step_sec)

        while current_time < end_time:
            # Simulate time step
            measurements, events, alerts = self.simulate_time_step(current_time)

            measurement_batch.extend(measurements)
            event_batch.extend(events)
            alert_batch.extend(alerts)

            # Insert in batches
            if len(measurement_batch) >= batch_size:
                self.db.measurements.insert_many(measurement_batch)
                total_measurements += len(measurement_batch)
                measurement_batch = []

            if event_batch:
                self.db.events.insert_many(event_batch)
                total_events += len(event_batch)
                event_batch = []

            if alert_batch:
                # Check for duplicate alerts before inserting
                for alert in alert_batch:
                    existing = self.db.alerts.find_one({
                        "assetId": alert["assetId"],
                        "alertType": alert["alertType"],
                        "status": "active"
                    })
                    if not existing:
                        self.db.alerts.insert_one(alert)
                        total_alerts += 1
                alert_batch = []

            # Progress update
            step_count += 1
            if step_count % 100 == 0:
                progress = (step_count / total_steps) * 100
                print(f"Progress: {progress:.1f}% - Measurements: {total_measurements}, "
                      f"Events: {total_events}, Alerts: {total_alerts}")

            # Advance time
            current_time += timedelta(seconds=base_step_sec)

        # Insert remaining batches
        if measurement_batch:
            self.db.measurements.insert_many(measurement_batch)
            total_measurements += len(measurement_batch)

        if event_batch:
            self.db.events.insert_many(event_batch)
            total_events += len(event_batch)

        for alert in alert_batch:
            existing = self.db.alerts.find_one({
                "assetId": alert["assetId"],
                "alertType": alert["alertType"],
                "status": "active"
            })
            if not existing:
                self.db.alerts.insert_one(alert)
                total_alerts += 1

        # Summary
        print("\n" + "="*50)
        print("Simulation Complete!")
        print(f"Duration: {duration_hours} hours")
        print(f"Measurements generated: {total_measurements}")
        print(f"Events generated: {total_events}")
        print(f"Alerts generated: {total_alerts}")
        print(f"Average measurements/hour: {total_measurements/duration_hours:.1f}")
        print("="*50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simulate cold chain monitoring data")
    parser.add_argument("--hours", type=float, default=1,
                      help="Duration of simulation in hours")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--base-step-sec", type=int, default=60,
                      help="Base time step in seconds")
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
    simulator = ColdChainSimulator(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    simulator.run_simulation(
        duration_hours=args.hours,
        base_step_sec=args.base_step_sec
    )


if __name__ == "__main__":
    main()