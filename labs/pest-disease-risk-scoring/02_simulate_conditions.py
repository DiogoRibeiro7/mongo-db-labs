#!/usr/bin/env python3
"""
Agricultural Pest & Disease Risk Scoring - Conditions Simulation
Simulates weather conditions, pest populations, and calculates risk scores
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
import random
import argparse
import time
import math
import numpy as np

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "agrimonitor_db"


class AgriculturalSimulator:
    """Simulates agricultural conditions and risk assessments."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize simulator."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

        # Load infrastructure
        self.farms = list(self.db.farms.find({"status": "active"}))
        self.fields = list(self.db.fields.find({"status": {"$in": ["planted", "growing", "harvesting"]}}))
        self.sensors = list(self.db.sensors.find({"status": "active"}))

        if not self.farms:
            print("No farms found. Please run seed script first.")
            sys.exit(1)

        if not self.fields:
            print("No fields found. Please run seed script first.")
            sys.exit(1)

        if not self.sensors:
            print("No sensors found. Please run seed script first.")
            sys.exit(1)

        print(f"Loaded {len(self.farms)} farms, {len(self.fields)} fields, {len(self.sensors)} sensors")

        # Build sensor mappings
        self.field_sensors = {}
        for sensor in self.sensors:
            field_id = sensor.get("fieldId")
            if field_id:
                if field_id not in self.field_sensors:
                    self.field_sensors[field_id] = {}
                sensor_type = sensor["type"]
                if sensor_type not in self.field_sensors[field_id]:
                    self.field_sensors[field_id][sensor_type] = []
                self.field_sensors[field_id][sensor_type].append(sensor)

        # Weather state per farm
        self.weather_state = {}
        for farm in self.farms:
            self.weather_state[farm["farmId"]] = {
                "temperature": 25.0,
                "humidity": 65.0,
                "rainfall_accumulation": 0.0,
                "weather_pattern": "stable"
            }

        # Pest population dynamics
        self.pest_state = {}
        for field in self.fields:
            self.pest_state[field["fieldId"]] = {
                "base_population": random.randint(2, 15),
                "growth_rate": random.uniform(0.05, 0.15),
                "last_spray_effect": 0
            }

    def get_weather_pattern(self, region, hour, day_of_year):
        """Generate realistic weather patterns based on region and time."""
        # Regional climate patterns
        climate_patterns = {
            "California Central Valley": {
                "temp_range": (10, 40),
                "humidity_range": (30, 80),
                "rain_probability": 0.05 if 150 < day_of_year < 300 else 0.15
            },
            "Iowa Corn Belt": {
                "temp_range": (-10, 35),
                "humidity_range": (40, 90),
                "rain_probability": 0.20 if 90 < day_of_year < 270 else 0.10
            },
            "Punjab": {
                "temp_range": (5, 45),
                "humidity_range": (20, 95),
                "rain_probability": 0.40 if 180 < day_of_year < 270 else 0.05  # Monsoon
            },
            "Queensland": {
                "temp_range": (10, 35),
                "humidity_range": (40, 85),
                "rain_probability": 0.25 if day_of_year < 90 or day_of_year > 330 else 0.10  # Summer rain
            }
        }

        # Get base pattern for region
        for pattern_key in climate_patterns:
            if pattern_key in region:
                pattern = climate_patterns[pattern_key]
                break
        else:
            pattern = {
                "temp_range": (5, 35),
                "humidity_range": (30, 90),
                "rain_probability": 0.15
            }

        # Daily temperature curve
        temp_min, temp_max = pattern["temp_range"]
        seasonal_adjust = 10 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        daily_temp = (temp_min + temp_max) / 2 + seasonal_adjust

        # Hourly variation
        hourly_variation = 5 * math.sin(2 * math.pi * (hour - 6) / 24)
        temperature = daily_temp + hourly_variation + random.gauss(0, 2)
        temperature = max(temp_min, min(temp_max, temperature))

        # Humidity inversely related to temperature
        humidity_base = 90 - (temperature - temp_min) / (temp_max - temp_min) * 40
        humidity = humidity_base + random.gauss(0, 10)
        humidity = max(pattern["humidity_range"][0], min(pattern["humidity_range"][1], humidity))

        # Rainfall probability
        rain = random.random() < pattern["rain_probability"]
        if rain:
            rainfall = np.random.exponential(5)  # mm, exponential distribution for rain amounts
        else:
            rainfall = 0

        return temperature, humidity, rainfall

    def calculate_leaf_wetness(self, humidity, temperature, rainfall, hour):
        """Calculate leaf wetness duration based on conditions."""
        # Base wetness from humidity and temperature (dew point)
        dew_point_diff = temperature - (temperature - (100 - humidity) / 5)

        if dew_point_diff < 2:  # Close to dew point
            base_wetness = 2.0
        elif dew_point_diff < 5:
            base_wetness = 1.0
        else:
            base_wetness = 0.0

        # Add wetness from rainfall
        if rainfall > 0:
            rain_wetness = min(8, rainfall / 2)  # Up to 8 hours from rain
        else:
            rain_wetness = 0

        # Night time increases wetness duration
        if hour < 6 or hour > 20:
            night_bonus = 1.5
        else:
            night_bonus = 0

        # High humidity extends wetness
        if humidity > 85:
            humidity_bonus = 2.0
        elif humidity > 75:
            humidity_bonus = 1.0
        else:
            humidity_bonus = 0

        total_wetness = base_wetness + rain_wetness + night_bonus + humidity_bonus

        # Add some randomness
        total_wetness += random.gauss(0, 0.5)

        return max(0, min(15, total_wetness))  # Cap at 15 hours

    def simulate_pest_population(self, field_id, temperature, humidity, rainfall):
        """Simulate pest population dynamics."""
        pest_state = self.pest_state[field_id]

        # Temperature effect on pest reproduction
        if 20 <= temperature <= 30:
            temp_factor = 1.2  # Optimal temperature
        elif 15 <= temperature <= 35:
            temp_factor = 1.0  # Moderate
        else:
            temp_factor = 0.5  # Poor conditions

        # Humidity effect
        if 60 <= humidity <= 80:
            humid_factor = 1.1
        else:
            humid_factor = 0.9

        # Rain effect (can wash away or help depending on pest)
        if rainfall > 20:
            rain_factor = 0.7  # Heavy rain reduces population
        elif rainfall > 0:
            rain_factor = 1.0
        else:
            rain_factor = 0.95  # Drought stress

        # Apply spray effect decay
        if pest_state["last_spray_effect"] > 0:
            pest_state["last_spray_effect"] *= 0.9  # 10% decay per interval

        # Calculate new population
        growth = pest_state["growth_rate"] * temp_factor * humid_factor * rain_factor
        new_population = pest_state["base_population"] * (1 + growth) * (1 - pest_state["last_spray_effect"])

        # Add randomness
        new_population += random.gauss(0, 2)

        # Update base population
        pest_state["base_population"] = max(0, min(100, new_population))

        return int(pest_state["base_population"])

    def calculate_risk_score(self, field, measurements):
        """Calculate comprehensive risk score with detailed explanation."""
        risk_components = {}
        explanation_parts = []

        # Get latest measurements
        leaf_wetness = measurements.get("leaf_wetness", 0)
        temperature = measurements.get("air_temperature", 20)
        humidity = measurements.get("relative_humidity", 60)
        rainfall = measurements.get("rainfall", 0)
        trap_count = measurements.get("trap_count", 0)

        # Get recent rainfall accumulation
        rainfall_24h = measurements.get("rainfall_24h", rainfall)
        rainfall_72h = measurements.get("rainfall_72h", rainfall)

        # Initialize risk score
        risk_score = 0

        # 1. Leaf Wetness Component (0-30 points)
        if leaf_wetness > 10:
            wetness_score = 30
            explanation_parts.append(f"CRITICAL: Leaf wetness of {leaf_wetness:.1f} hours exceeds 10-hour threshold for severe disease risk")
        elif leaf_wetness > 6:
            wetness_score = 20
            explanation_parts.append(f"WARNING: Leaf wetness of {leaf_wetness:.1f} hours (6-10h range) indicates moderate disease pressure")
        elif leaf_wetness > 3:
            wetness_score = 10
            explanation_parts.append(f"CAUTION: Leaf wetness of {leaf_wetness:.1f} hours (3-6h range) suggests low disease risk")
        else:
            wetness_score = 0
            explanation_parts.append(f"GOOD: Minimal leaf wetness ({leaf_wetness:.1f}h <3h) indicates very low disease risk")

        risk_components["leafWetness"] = {
            "value": leaf_wetness,
            "weight": 0.30,
            "contribution": wetness_score
        }
        risk_score += wetness_score

        # 2. Temperature Component (0-20 points)
        # Disease-favorable temperature ranges
        if 18 <= temperature <= 28:
            temp_score = 20
            optimal = True
            explanation_parts.append(f"ALERT: Temperature {temperature:.1f}°C is in optimal range (18-28°C) for most fungal pathogens")
        elif 15 <= temperature <= 32:
            temp_score = 10
            optimal = False
            explanation_parts.append(f"NOTE: Temperature {temperature:.1f}°C is in moderate risk range for pathogen development")
        else:
            temp_score = 0
            optimal = False
            explanation_parts.append(f"FAVORABLE: Temperature {temperature:.1f}°C is outside optimal range for most pathogens")

        risk_components["temperature"] = {
            "value": temperature,
            "weight": 0.20,
            "contribution": temp_score,
            "optimal": optimal
        }
        risk_score += temp_score

        # 3. Humidity Component (0-20 points)
        if humidity > 85:
            humid_score = 20
            explanation_parts.append(f"HIGH RISK: Relative humidity {humidity:.0f}% exceeds 85%, highly favorable for disease")
        elif humidity > 70:
            humid_score = 15
            explanation_parts.append(f"MODERATE: Humidity {humidity:.0f}% (70-85%) provides moderate disease pressure")
        elif humidity > 60:
            humid_score = 8
            explanation_parts.append(f"LOW: Humidity {humidity:.0f}% (60-70%) indicates low disease pressure")
        else:
            humid_score = 0
            explanation_parts.append(f"MINIMAL: Low humidity {humidity:.0f}% (<60%) inhibits disease development")

        risk_components["humidity"] = {
            "value": humidity,
            "weight": 0.20,
            "contribution": humid_score
        }
        risk_score += humid_score

        # 4. Rainfall Component (0-15 points)
        if rainfall_24h > 20:
            rain_score = 15
            explanation_parts.append(f"SEVERE: Heavy rainfall ({rainfall_24h:.1f}mm/24h) greatly increases disease spread")
        elif rainfall_24h > 10:
            rain_score = 10
            explanation_parts.append(f"MODERATE: Recent rainfall ({rainfall_24h:.1f}mm/24h) may facilitate disease spread")
        elif rainfall_24h > 2:
            rain_score = 5
            explanation_parts.append(f"LOW: Light rainfall ({rainfall_24h:.1f}mm/24h) poses minimal disease risk")
        else:
            rain_score = 0
            explanation_parts.append(f"DRY: No significant rainfall ({rainfall_24h:.1f}mm/24h) reduces disease spread")

        risk_components["rainfall"] = {
            "value": rainfall_24h,
            "weight": 0.15,
            "contribution": rain_score,
            "recent24h": rainfall_24h,
            "recent72h": rainfall_72h
        }
        risk_score += rain_score

        # 5. Pest Pressure Component (0-15 points)
        # Dynamic threshold based on crop and growth stage
        crop_type = field.get("crop", {}).get("type", "unknown")
        growth_stage = field.get("crop", {}).get("growthStage", "unknown")

        # Adjust threshold based on growth stage
        base_threshold = 10
        if growth_stage in ["flowering", "fruiting"]:
            threshold = base_threshold * 0.7  # More sensitive during critical stages
        else:
            threshold = base_threshold

        if trap_count > threshold * 3:
            trap_score = 15
            trend = "increasing"
            explanation_parts.append(f"OUTBREAK: Pest count {trap_count} is 3x above threshold ({threshold:.0f}), immediate action required")
        elif trap_count > threshold * 2:
            trap_score = 10
            trend = "increasing"
            explanation_parts.append(f"HIGH: Pest count {trap_count} is 2x above threshold ({threshold:.0f}), action recommended")
        elif trap_count > threshold:
            trap_score = 5
            trend = "stable"
            explanation_parts.append(f"THRESHOLD: Pest count {trap_count} exceeds economic threshold ({threshold:.0f})")
        else:
            trap_score = 0
            trend = "decreasing"
            explanation_parts.append(f"CONTROLLED: Pest count {trap_count} below threshold ({threshold:.0f})")

        risk_components["trapCount"] = {
            "value": trap_count,
            "weight": 0.15,
            "contribution": trap_score,
            "trend": trend,
            "threshold": threshold
        }
        risk_score += trap_score

        # Determine overall risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Final explanation summary
        explanation = f"Risk Score: {risk_score}/100 ({risk_level.upper()}). " + " | ".join(explanation_parts[:3])

        return risk_score, risk_level, risk_components, explanation

    def generate_measurement(self, sensor, field, timestamp, weather_state, pest_population):
        """Generate a measurement for a sensor."""
        sensor_type = sensor["type"]

        # Base measurement structure
        measurement = {
            "timestamp": timestamp,
            "meta": {
                "sensorId": sensor["sensorId"],
                "fieldId": field["fieldId"],
                "farmId": field["farmId"],
                "sensorType": sensor_type
            }
        }

        # Generate sensor-specific readings
        if sensor_type == "air_temperature":
            measurement["value"] = weather_state["temperature"]
            measurement["unit"] = "celsius"

        elif sensor_type == "relative_humidity":
            measurement["value"] = weather_state["humidity"]
            measurement["unit"] = "percent"

        elif sensor_type == "rainfall":
            measurement["value"] = weather_state.get("current_rainfall", 0)
            measurement["unit"] = "mm"
            measurement["accumulation24h"] = weather_state.get("rainfall_accumulation", 0)

        elif sensor_type == "leaf_wetness":
            measurement["value"] = weather_state.get("leaf_wetness", 0)
            measurement["unit"] = "hours"
            measurement["wetness_index"] = min(15, measurement["value"]) / 15 * 100  # 0-100 scale

        elif sensor_type == "trap_count":
            # Only update trap counts once per day
            if timestamp.hour == 6:  # Morning check
                measurement["value"] = pest_population
                measurement["unit"] = "count"
                measurement["trapId"] = sensor["sensorId"]
                measurement["pestType"] = sensor.get("trapDetails", {}).get("targetPest", "Unknown")
            else:
                return None  # Skip non-morning readings for traps

        elif sensor_type == "wind_speed":
            # Simulate wind speed
            base_wind = random.uniform(0, 20)
            measurement["value"] = base_wind + random.gauss(0, 2)
            measurement["unit"] = "km/h"
            measurement["direction"] = random.randint(0, 360)

        elif sensor_type == "soil_moisture":
            # Soil moisture affected by rainfall
            base_moisture = 30 + weather_state.get("rainfall_accumulation", 0) * 2
            measurement["value"] = min(100, base_moisture + random.gauss(0, 5))
            measurement["unit"] = "percent"

        # Add quality metrics
        measurement["quality"] = {
            "signalStrength": sensor["connectivity"]["signalStrength"] + random.randint(-5, 5),
            "batteryLevel": sensor["connectivity"]["batteryLevel"] - random.uniform(0, 0.1),
            "reliability": random.uniform(95, 100)
        }

        return measurement

    def generate_risk_assessment(self, field, measurements, timestamp):
        """Generate a comprehensive risk assessment."""
        assessment_counter = int(timestamp.timestamp() * 1000000)

        # Calculate risk score
        risk_score, risk_level, risk_components, explanation = self.calculate_risk_score(field, measurements)

        # Determine recommendation based on risk level
        if risk_level == "critical":
            action = "immediate_action"
            priority = "urgent"
            timing = "Within 12 hours"
        elif risk_level == "high":
            action = "curative_spray"
            priority = "high"
            timing = "Within 24 hours"
        elif risk_level == "moderate":
            action = "preventive_spray"
            priority = "medium"
            timing = "Within 48 hours"
        else:
            action = "monitor_closely"
            priority = "low"
            timing = "Continue monitoring"

        # Get common diseases and pests for this field
        common_diseases = field.get("riskHistory", {}).get("commonDiseases", ["Generic Disease"])
        common_pests = field.get("riskHistory", {}).get("commonPests", ["Generic Pest"])

        # Create assessment
        assessment = {
            "assessmentId": f"RSK{assessment_counter % 1000000000000:012d}",
            "fieldId": field["fieldId"],
            "farmId": field["farmId"],
            "timestamp": timestamp,
            "riskScore": risk_score,
            "riskLevel": risk_level,
            "factors": risk_components,
            "diseases": [
                {
                    "name": disease,
                    "probability": min(100, risk_score * 0.9 + random.uniform(-10, 10)),
                    "conditions_met": sum([
                        risk_components["leafWetness"]["contribution"] > 10,
                        risk_components["temperature"].get("optimal", False),
                        risk_components["humidity"]["contribution"] > 10,
                        risk_components["rainfall"]["contribution"] > 5
                    ]),
                    "total_conditions": 4
                }
                for disease in common_diseases[:2]
            ],
            "pests": [
                {
                    "name": pest,
                    "population": "outbreak" if risk_components["trapCount"]["value"] > risk_components["trapCount"]["threshold"] * 3
                                  else "high" if risk_components["trapCount"]["value"] > risk_components["trapCount"]["threshold"] * 2
                                  else "moderate" if risk_components["trapCount"]["value"] > risk_components["trapCount"]["threshold"]
                                  else "low",
                    "trapCount": int(risk_components["trapCount"]["value"]),
                    "economicThreshold": int(risk_components["trapCount"]["threshold"])
                }
                for pest in common_pests[:2]
            ],
            "recommendation": {
                "action": action,
                "priority": priority,
                "products": self.get_recommended_products(field, risk_level, common_diseases, common_pests) if action != "monitor_closely" else [],
                "timing": timing,
                "notes": f"Assessment based on current environmental conditions and pest pressure. {explanation.split('.')[0]}."
            },
            "explanation": explanation,
            "confidence": min(95, 70 + risk_score * 0.25)  # Higher risk = higher confidence
        }

        return assessment

    def get_recommended_products(self, field, risk_level, diseases, pests):
        """Get recommended products based on risk and pest/disease type."""
        products = []

        # Fungicide recommendations
        if risk_level in ["high", "critical"]:
            fungicides = {
                "Rust": {"name": "Propiconazole", "dosage": "1.5 L/ha", "rei": 24, "phi": 30},
                "Powdery Mildew": {"name": "Azoxystrobin", "dosage": "2.0 L/ha", "rei": 12, "phi": 14},
                "Downy Mildew": {"name": "Mancozeb", "dosage": "2.5 kg/ha", "rei": 24, "phi": 21},
                "Blight": {"name": "Chlorothalonil", "dosage": "2.0 L/ha", "rei": 48, "phi": 14}
            }

            for disease in diseases:
                for key in fungicides:
                    if key.lower() in disease.lower():
                        product = fungicides[key].copy()
                        product["type"] = "fungicide"
                        products.append(product)
                        break

            # Default fungicide if no specific match
            if not products:
                products.append({
                    "name": "Copper Hydroxide",
                    "type": "fungicide",
                    "dosage": "3.0 kg/ha",
                    "rei": 24,
                    "phi": 7
                })

        # Insecticide recommendations
        if len(pests) > 0 and risk_level != "low":
            insecticides = {
                "Aphids": {"name": "Imidacloprid", "dosage": "0.5 L/ha", "rei": 12, "phi": 21},
                "Armyworm": {"name": "Chlorpyrifos", "dosage": "1.5 L/ha", "rei": 24, "phi": 21},
                "Borer": {"name": "Spinosad", "dosage": "1.0 L/ha", "rei": 4, "phi": 7},
                "Whitefly": {"name": "Spiromesifen", "dosage": "0.75 L/ha", "rei": 12, "phi": 14}
            }

            for pest in pests:
                for key in insecticides:
                    if key.lower() in pest.lower():
                        product = insecticides[key].copy()
                        product["type"] = "insecticide"
                        products.append(product)
                        break

        return products[:2]  # Limit to 2 products

    def generate_event(self, assessment, timestamp):
        """Generate event based on risk assessment."""
        if assessment["riskLevel"] not in ["high", "critical"]:
            return None

        event_counter = int(timestamp.timestamp() * 1000000)

        event_type = "SPRAY_RECOMMENDATION" if assessment["riskLevel"] == "critical" else "RISK_ALERT"

        event = {
            "eventId": f"EVT{event_counter % 1000000000000:012d}",
            "eventType": event_type,
            "fieldId": assessment["fieldId"],
            "farmId": assessment["farmId"],
            "timestamp": timestamp,
            "endTime": None,
            "severity": "critical" if assessment["riskLevel"] == "critical" else "warning",
            "details": {
                "riskScore": assessment["riskScore"],
                "affectedArea": random.uniform(5, 20),
                "diseaseName": assessment["diseases"][0]["name"] if assessment["diseases"] else None,
                "pestName": assessment["pests"][0]["name"] if assessment["pests"] else None,
                "trapCount": assessment["factors"]["trapCount"]["value"],
                "conditions": {
                    "leafWetness": assessment["factors"]["leafWetness"]["value"],
                    "temperature": assessment["factors"]["temperature"]["value"],
                    "humidity": assessment["factors"]["humidity"]["value"],
                    "rainfall": assessment["factors"]["rainfall"]["value"]
                },
                "recommendedAction": assessment["recommendation"]["action"],
                "economicImpact": random.uniform(5000, 20000) if assessment["riskLevel"] == "critical" else random.uniform(1000, 5000)
            },
            "response": None,
            "acknowledged": False,
            "acknowledgedBy": None,
            "acknowledgedAt": None,
            "notifications": [
                {
                    "method": "app",
                    "recipient": f"farm-{assessment['farmId'][-3:]}@agrimonitor.com",
                    "sentAt": timestamp,
                    "status": "delivered"
                }
            ]
        }

        return event

    def simulate_time_step(self, current_time):
        """Simulate one time step for all fields."""
        measurements = []
        assessments = []
        events = []

        hour = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        # Group fields by farm
        farm_fields = {}
        for field in self.fields:
            farm_id = field["farmId"]
            if farm_id not in farm_fields:
                farm_fields[farm_id] = []
            farm_fields[farm_id].append(field)

        # Process each farm
        for farm in self.farms:
            farm_id = farm["farmId"]
            if farm_id not in farm_fields:
                continue

            # Get weather for this farm
            region = farm["location"]["region"]
            temperature, humidity, rainfall = self.get_weather_pattern(region, hour, day_of_year)

            # Update weather state
            weather_state = self.weather_state[farm_id]
            weather_state["temperature"] = temperature
            weather_state["humidity"] = humidity
            weather_state["current_rainfall"] = rainfall
            weather_state["rainfall_accumulation"] += rainfall

            # Calculate leaf wetness
            leaf_wetness = self.calculate_leaf_wetness(humidity, temperature, rainfall, hour)
            weather_state["leaf_wetness"] = leaf_wetness

            # Decay rainfall accumulation
            if hour == 0:  # Reset daily at midnight
                weather_state["rainfall_accumulation"] *= 0.5

            # Process each field in this farm
            for field in farm_fields[farm_id]:
                field_id = field["fieldId"]

                # Get sensors for this field
                if field_id not in self.field_sensors:
                    continue

                # Simulate pest population
                pest_population = self.simulate_pest_population(field_id, temperature, humidity, rainfall)

                # Collect measurements from all sensors
                field_measurements = {
                    "air_temperature": temperature,
                    "relative_humidity": humidity,
                    "rainfall": rainfall,
                    "rainfall_24h": weather_state["rainfall_accumulation"],
                    "rainfall_72h": weather_state["rainfall_accumulation"] * 1.5,  # Approximation
                    "leaf_wetness": leaf_wetness,
                    "trap_count": pest_population
                }

                # Generate measurements for each sensor
                for sensor_type, sensors in self.field_sensors[field_id].items():
                    for sensor in sensors:
                        if sensor["status"] != "active":
                            continue

                        measurement = self.generate_measurement(
                            sensor, field, current_time, weather_state, pest_population
                        )
                        if measurement:
                            measurements.append(measurement)

                # Generate risk assessment every 6 hours
                if hour % 6 == 0:
                    assessment = self.generate_risk_assessment(field, field_measurements, current_time)
                    assessments.append(assessment)

                    # Generate event if needed
                    event = self.generate_event(assessment, current_time)
                    if event:
                        events.append(event)

                        # Simulate spray response
                        if assessment["riskLevel"] == "critical" and random.random() > 0.3:
                            self.pest_state[field_id]["last_spray_effect"] = 0.8  # 80% reduction

        return measurements, assessments, events

    def run_simulation(self, duration_hours=1, interval_minutes=60):
        """Run the simulation for specified duration."""
        print(f"\nStarting agricultural conditions simulation for {duration_hours} hours...")
        print(f"Measurement interval: {interval_minutes} minutes")

        start_time = datetime.now()
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)

        total_measurements = 0
        total_assessments = 0
        total_events = 0

        batch_size = 1000
        measurement_batch = []
        assessment_batch = []
        event_batch = []

        step_count = 0
        total_steps = int(duration_hours * 60 / interval_minutes)

        while current_time < end_time:
            # Simulate time step
            measurements, assessments, events = self.simulate_time_step(current_time)

            measurement_batch.extend(measurements)
            assessment_batch.extend(assessments)
            event_batch.extend(events)

            # Insert in batches
            if len(measurement_batch) >= batch_size:
                self.db.measurements.insert_many(measurement_batch)
                total_measurements += len(measurement_batch)
                measurement_batch = []

            if assessment_batch:
                self.db.risk_assessments.insert_many(assessment_batch)
                total_assessments += len(assessment_batch)
                assessment_batch = []

            if event_batch:
                self.db.events.insert_many(event_batch)
                total_events += len(event_batch)
                event_batch = []

            # Progress update
            step_count += 1
            if step_count % 10 == 0:
                progress = (step_count / total_steps) * 100
                print(f"Progress: {progress:.1f}% - Measurements: {total_measurements}, "
                      f"Assessments: {total_assessments}, Events: {total_events}")

                # Show risk summary
                if assessments:
                    risk_summary = {}
                    for assessment in assessments[-10:]:
                        level = assessment["riskLevel"]
                        risk_summary[level] = risk_summary.get(level, 0) + 1
                    print(f"  Recent risk levels: {risk_summary}")

            # Advance time
            current_time += timedelta(minutes=interval_minutes)

        # Insert remaining batches
        if measurement_batch:
            self.db.measurements.insert_many(measurement_batch)
            total_measurements += len(measurement_batch)

        if assessment_batch:
            self.db.risk_assessments.insert_many(assessment_batch)
            total_assessments += len(assessment_batch)

        if event_batch:
            self.db.events.insert_many(event_batch)
            total_events += len(event_batch)

        # Summary
        print("\n" + "="*50)
        print("Simulation Complete!")
        print(f"Duration: {duration_hours} hours")
        print(f"Measurements generated: {total_measurements}")
        print(f"Risk assessments: {total_assessments}")
        print(f"Events generated: {total_events}")
        print(f"Average measurements/hour: {total_measurements/duration_hours:.1f}")

        # Field statistics
        print("\nField Risk Summary:")
        risk_counts = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        recent_assessments = list(self.db.risk_assessments.find().sort("timestamp", -1).limit(len(self.fields)))
        for assessment in recent_assessments:
            risk_counts[assessment["riskLevel"]] = risk_counts.get(assessment["riskLevel"], 0) + 1

        for level, count in risk_counts.items():
            percentage = (count / len(self.fields) * 100) if self.fields else 0
            print(f"  {level.capitalize()}: {count} fields ({percentage:.1f}%)")

        print("="*50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simulate agricultural conditions")
    parser.add_argument("--hours", type=float, default=1,
                      help="Duration of simulation in hours")
    parser.add_argument("--interval", type=int, default=60,
                      help="Measurement interval in minutes")
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
    simulator = AgriculturalSimulator(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    simulator.run_simulation(
        duration_hours=args.hours,
        interval_minutes=args.interval
    )


if __name__ == "__main__":
    main()