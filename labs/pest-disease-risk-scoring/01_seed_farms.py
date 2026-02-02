#!/usr/bin/env python3
"""
Agricultural Pest & Disease Risk Scoring - Farm Infrastructure Seeding
Seeds farms, fields, and monitoring sensors
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB connection settings
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "agrimonitor_db"


class AgriculturalSeeder:
    """Seeds agricultural monitoring infrastructure data."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize seeder with MongoDB connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

    def clean_collections(self):
        """Remove existing data from all collections."""
        collections = ["farms", "fields", "sensors", "risk_assessments", "events"]
        for coll in collections:
            count = self.db[coll].delete_many({}).deleted_count
            if count > 0:
                print(f"Cleaned {count} documents from {coll}")

    def seed_farms(self):
        """Seed multiple farms with different characteristics."""
        farms = []

        # Farm templates with regional characteristics
        farm_templates = [
            {
                "region": "California Central Valley",
                "country": "USA",
                "lat_base": 36.7783,
                "lng_base": -119.4179,
                "elevation": 100,
                "primary_crops": ["grape", "citrus", "tomato", "vegetables"],
                "climate": "Mediterranean"
            },
            {
                "region": "Iowa Corn Belt",
                "country": "USA",
                "lat_base": 42.0308,
                "lng_base": -93.6319,
                "elevation": 300,
                "primary_crops": ["corn", "soybean", "wheat"],
                "climate": "Continental"
            },
            {
                "region": "Punjab",
                "country": "India",
                "lat_base": 31.1471,
                "lng_base": 75.3412,
                "elevation": 200,
                "primary_crops": ["wheat", "rice", "cotton"],
                "climate": "Subtropical"
            },
            {
                "region": "Queensland",
                "country": "Australia",
                "lat_base": -27.4698,
                "lng_base": 153.0251,
                "elevation": 50,
                "primary_crops": ["citrus", "grape", "vegetables", "cotton"],
                "climate": "Subtropical"
            }
        ]

        farm_counter = 1
        for template in farm_templates:
            # Create 2-3 farms per region
            num_farms = random.randint(2, 3)
            for i in range(num_farms):
                farm_id = f"FRM{farm_counter:06d}"

                # Vary location slightly within region
                lat = template["lat_base"] + random.uniform(-0.5, 0.5)
                lng = template["lng_base"] + random.uniform(-0.5, 0.5)

                # Farm size varies by region and type
                if template["climate"] in ["Mediterranean", "Subtropical"]:
                    total_size = random.uniform(50, 500)  # Smaller, intensive farms
                else:
                    total_size = random.uniform(200, 2000)  # Larger grain farms

                farm = {
                    "farmId": farm_id,
                    "name": f"{template['region']} Farm {farm_counter}",
                    "owner": {
                        "name": f"Farmer {random.choice(['Smith', 'Johnson', 'Patel', 'Chen', 'Williams', 'Brown'])}",
                        "contact": f"+1{random.randint(1000000000, 9999999999)}",
                        "email": f"farm{farm_counter}@agrimonitor.com"
                    },
                    "location": {
                        "type": "Point",
                        "coordinates": [lng, lat],
                        "region": template["region"],
                        "country": template["country"],
                        "elevation": template["elevation"] + random.uniform(-20, 20)
                    },
                    "size": {
                        "total": total_size,
                        "cultivated": total_size * random.uniform(0.75, 0.95),
                        "unit": "hectares"
                    },
                    "certification": {
                        "organic": random.choice([True, False, False]),  # 33% organic
                        "globalGAP": random.choice([True, True, False]),  # 66% GAP certified
                        "fairTrade": random.choice([True, False]),
                        "certifications": random.sample(
                            ["ISO 22000", "HACCP", "SQF", "BRC", "USDA Organic"],
                            k=random.randint(0, 3)
                        )
                    },
                    "management": {
                        "ipmEnabled": random.choice([True, True, False]),  # 66% IPM
                        "sprayProtocol": random.choice(["integrated", "preventive", "curative", "organic"]),
                        "monitoringFrequency": random.choice(["daily", "twice_weekly", "weekly"])
                    },
                    "status": "active",
                    "createdAt": datetime.now() - timedelta(days=random.randint(365, 1825)),
                    "updatedAt": datetime.now() - timedelta(days=random.randint(1, 30))
                }

                farms.append(farm)
                farm_counter += 1

        # Insert farms
        if farms:
            result = self.db.farms.insert_many(farms)
            print(f"Seeded {len(result.inserted_ids)} farms")

        return farms

    def seed_fields(self, farms):
        """Seed fields for each farm."""
        fields = []
        field_counter = 1

        for farm in farms:
            # Number of fields depends on farm size
            farm_size = farm["size"]["total"]
            if farm_size < 100:
                num_fields = random.randint(2, 5)
            elif farm_size < 500:
                num_fields = random.randint(5, 10)
            else:
                num_fields = random.randint(10, 20)

            # Get region-appropriate crops
            region = farm["location"]["region"]
            if "California" in region or "Queensland" in region:
                crop_options = ["grape", "citrus", "tomato", "vegetables"]
            elif "Iowa" in region:
                crop_options = ["corn", "soybean", "wheat"]
            elif "Punjab" in region:
                crop_options = ["wheat", "rice", "cotton"]
            else:
                crop_options = ["wheat", "corn", "soybean", "vegetables"]

            # Calculate field sizes
            avg_field_size = farm["size"]["cultivated"] / num_fields

            for i in range(num_fields):
                field_id = f"FLD{field_counter:08d}"

                # Select crop for this field
                crop_type = random.choice(crop_options)

                # Crop-specific varieties
                varieties = {
                    "wheat": ["Winter Red", "Spring White", "Durum"],
                    "corn": ["Yellow Dent", "Sweet Corn", "White Corn"],
                    "soybean": ["Roundup Ready", "Liberty Link", "Conventional"],
                    "rice": ["Basmati", "Jasmine", "Long Grain"],
                    "cotton": ["Upland", "Pima", "Organic"],
                    "grape": ["Chardonnay", "Cabernet", "Pinot Noir", "Table Grape"],
                    "citrus": ["Orange", "Lemon", "Grapefruit", "Mandarin"],
                    "tomato": ["Roma", "Cherry", "Beefsteak", "Heirloom"],
                    "potato": ["Russet", "Red", "Gold", "Fingerling"],
                    "vegetables": ["Mixed Greens", "Broccoli", "Carrots", "Peppers"]
                }

                variety = random.choice(varieties.get(crop_type, ["Standard"]))

                # Planting date based on crop and region
                if crop_type in ["wheat", "rice"]:
                    planting_date = datetime.now() - timedelta(days=random.randint(30, 120))
                else:
                    planting_date = datetime.now() - timedelta(days=random.randint(60, 150))

                # Growth stage based on planting date
                days_since_planting = (datetime.now() - planting_date).days
                if days_since_planting < 20:
                    growth_stage = "seedling"
                elif days_since_planting < 50:
                    growth_stage = "vegetative"
                elif days_since_planting < 80:
                    growth_stage = "flowering"
                elif days_since_planting < 110:
                    growth_stage = "fruiting"
                else:
                    growth_stage = "maturity"

                # Common pests and diseases by crop
                pest_disease_map = {
                    "wheat": {
                        "pests": ["Aphids", "Armyworm", "Hessian Fly"],
                        "diseases": ["Rust", "Powdery Mildew", "Fusarium Head Blight"]
                    },
                    "corn": {
                        "pests": ["Corn Borer", "Rootworm", "Armyworm"],
                        "diseases": ["Gray Leaf Spot", "Northern Corn Leaf Blight", "Tar Spot"]
                    },
                    "grape": {
                        "pests": ["Grape Phylloxera", "Japanese Beetle", "Grape Berry Moth"],
                        "diseases": ["Powdery Mildew", "Downy Mildew", "Botrytis"]
                    },
                    "citrus": {
                        "pests": ["Citrus Psyllid", "Scale", "Mites"],
                        "diseases": ["Citrus Canker", "Greening", "Root Rot"]
                    },
                    "tomato": {
                        "pests": ["Hornworm", "Aphids", "Whitefly"],
                        "diseases": ["Late Blight", "Early Blight", "Bacterial Spot"]
                    }
                }

                pest_disease = pest_disease_map.get(crop_type, {
                    "pests": ["Generic Pest A", "Generic Pest B"],
                    "diseases": ["Generic Disease A", "Generic Disease B"]
                })

                field = {
                    "fieldId": field_id,
                    "farmId": farm["farmId"],
                    "name": f"Field {chr(65 + i)}-{i+1}",
                    "crop": {
                        "type": crop_type,
                        "variety": variety,
                        "growthStage": growth_stage
                    },
                    "area": {
                        "size": avg_field_size * random.uniform(0.7, 1.3),
                        "unit": "hectares",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                # Create a proper closed polygon (5 points, first and last are the same)
                                [farm["location"]["coordinates"][0] - 0.005,
                                 farm["location"]["coordinates"][1] - 0.005],
                                [farm["location"]["coordinates"][0] + 0.005,
                                 farm["location"]["coordinates"][1] - 0.005],
                                [farm["location"]["coordinates"][0] + 0.005,
                                 farm["location"]["coordinates"][1] + 0.005],
                                [farm["location"]["coordinates"][0] - 0.005,
                                 farm["location"]["coordinates"][1] + 0.005],
                                [farm["location"]["coordinates"][0] - 0.005,
                                 farm["location"]["coordinates"][1] - 0.005]  # Close the polygon
                            ]]
                        }
                    },
                    "soil": {
                        "type": random.choice(["loam", "clay", "sandy", "silt"]),
                        "pH": random.uniform(5.5, 7.5),
                        "organic_matter": random.uniform(2, 6),
                        "drainage": random.choice(["excellent", "good", "moderate"])
                    },
                    "irrigation": {
                        "type": random.choice(["drip", "sprinkler", "pivot", "rainfed"]),
                        "automated": random.choice([True, False]),
                        "schedule": random.choice(["daily", "alternate", "weekly", "as_needed"])
                    },
                    "plantingDate": planting_date,
                    "expectedHarvest": planting_date + timedelta(days=random.randint(120, 180)),
                    "lastSpray": {
                        "date": datetime.now() - timedelta(days=random.randint(7, 30)),
                        "product": random.choice(["Fungicide A", "Insecticide B", "Herbicide C"]),
                        "reason": random.choice(["preventive", "curative", "scheduled"]),
                        "effectiveness": random.choice(["excellent", "good", "moderate"])
                    } if random.random() > 0.3 else None,
                    "status": "growing" if growth_stage != "maturity" else "harvesting",
                    "riskHistory": {
                        "lastHighRisk": datetime.now() - timedelta(days=random.randint(10, 60)),
                        "totalSprayEvents": random.randint(2, 12),
                        "commonPests": random.sample(pest_disease["pests"], k=random.randint(1, 2)),
                        "commonDiseases": random.sample(pest_disease["diseases"], k=random.randint(1, 2))
                    }
                }

                fields.append(field)
                field_counter += 1

        # Insert fields
        if fields:
            result = self.db.fields.insert_many(fields)
            print(f"Seeded {len(result.inserted_ids)} fields")

        return fields

    def seed_sensors(self, fields, farms):
        """Seed various types of sensors for fields."""
        sensors = []
        sensor_counter = 1

        # Build farm lookup
        farm_lookup = {farm["farmId"]: farm for farm in farms}

        for field in fields:
            farm = farm_lookup.get(field["farmId"])
            if not farm:
                continue

            # Each field gets a standard weather station
            weather_sensors = [
                ("air_temperature", "Davis Vantage Pro", None),
                ("relative_humidity", "Davis Vantage Pro", None),
                ("rainfall", "Rain Gauge RG-100", None),
                ("wind_speed", "Anemometer WS-200", None)
            ]

            for sensor_type, model, subtype in weather_sensors:
                sensor_id = f"SEN{sensor_counter:010d}"
                sensors.append({
                    "sensorId": sensor_id,
                    "type": sensor_type,
                    "subType": subtype,
                    "fieldId": field["fieldId"],
                    "farmId": field["farmId"],
                    "location": {
                        "coordinates": [
                            farm["location"]["coordinates"][0] + random.uniform(-0.001, 0.001),
                            farm["location"]["coordinates"][1] + random.uniform(-0.001, 0.001)
                        ],
                        "height": 2.0 if sensor_type != "rainfall" else 0.5,
                        "position": f"Field {field['name']} - Weather Station"
                    },
                    "manufacturer": "Davis Instruments",
                    "model": model,
                    "status": random.choices(
                        ["active", "maintenance", "faulty"],
                        weights=[0.9, 0.08, 0.02]
                    )[0],
                    "specifications": {
                        "accuracy": random.uniform(95, 99),
                        "range": {
                            "min": float(-40 if sensor_type == "air_temperature" else 0),
                            "max": float(60 if sensor_type == "air_temperature" else 100)
                        },
                        "measurementInterval": 15  # minutes
                    },
                    "connectivity": {
                        "protocol": "LoRa",
                        "batteryLevel": random.randint(60, 100),
                        "lastCommunication": datetime.now() - timedelta(minutes=random.randint(0, 30)),
                        "signalStrength": random.randint(-80, -40)
                    },
                    "calibration": {
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 180)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(30, 180)),
                        "offset": random.uniform(-0.5, 0.5)
                    },
                    "trapDetails": None,
                    "installedAt": field["plantingDate"] - timedelta(days=random.randint(7, 30)),
                    "replacedAt": None
                })
                sensor_counter += 1

            # Leaf wetness sensors (critical for disease prediction)
            num_leaf_sensors = random.randint(1, 3)
            for i in range(num_leaf_sensors):
                sensor_id = f"SEN{sensor_counter:010d}"
                sensors.append({
                    "sensorId": sensor_id,
                    "type": "leaf_wetness",
                    "subType": "resistance_grid",
                    "fieldId": field["fieldId"],
                    "farmId": field["farmId"],
                    "location": {
                        "coordinates": [
                            farm["location"]["coordinates"][0] + random.uniform(-0.001, 0.001),
                            farm["location"]["coordinates"][1] + random.uniform(-0.001, 0.001)
                        ],
                        "height": 1.0,  # Canopy height
                        "position": f"Field {field['name']} - Section {i+1}"
                    },
                    "manufacturer": "METER Group",
                    "model": "PHYTOS 31",
                    "status": "active",
                    "specifications": {
                        "accuracy": random.uniform(92, 98),
                        "range": {"min": 0.0, "max": 15.0},  # Wetness scale
                        "measurementInterval": 10
                    },
                    "connectivity": {
                        "protocol": "LoRa",
                        "batteryLevel": random.randint(70, 100),
                        "lastCommunication": datetime.now() - timedelta(minutes=random.randint(0, 20)),
                        "signalStrength": random.randint(-75, -45)
                    },
                    "calibration": {
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 90)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(60, 120)),
                        "offset": 0.0
                    },
                    "trapDetails": None,
                    "installedAt": field["plantingDate"],
                    "replacedAt": None
                })
                sensor_counter += 1

            # Pest traps (based on crop type)
            crop_type = field["crop"]["type"]
            target_pests = field["riskHistory"]["commonPests"]

            num_traps = random.randint(1, min(3, len(target_pests)))
            for i in range(num_traps):
                sensor_id = f"SEN{sensor_counter:010d}"
                target_pest = target_pests[i % len(target_pests)]

                sensors.append({
                    "sensorId": sensor_id,
                    "type": "trap_count",
                    "subType": f"{target_pest} Trap",
                    "fieldId": field["fieldId"],
                    "farmId": field["farmId"],
                    "location": {
                        "coordinates": [
                            farm["location"]["coordinates"][0] + random.uniform(-0.002, 0.002),
                            farm["location"]["coordinates"][1] + random.uniform(-0.002, 0.002)
                        ],
                        "height": 1.5,
                        "position": f"Field {field['name']} - Trap {i+1}"
                    },
                    "manufacturer": "Trece Inc",
                    "model": "Pherocon Trap",
                    "status": "active",
                    "specifications": {
                        "accuracy": 100.0,  # Manual count
                        "range": {"min": 0.0, "max": 500.0},
                        "measurementInterval": 1440  # Daily
                    },
                    "connectivity": {
                        "protocol": "cellular",
                        "batteryLevel": random.randint(80, 100),
                        "lastCommunication": datetime.now() - timedelta(hours=random.randint(0, 24)),
                        "signalStrength": random.randint(-70, -50)
                    },
                    "calibration": {
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 90)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(30, 90)),
                        "offset": 0.0  # No offset for trap counts
                    },
                    "trapDetails": {
                        "targetPest": target_pest,
                        "lureType": f"{target_pest} Pheromone",
                        "lureExpiry": datetime.now() + timedelta(days=random.randint(30, 90)),
                        "trapCapacity": 500
                    },
                    "installedAt": field["plantingDate"] + timedelta(days=random.randint(14, 30)),
                    "replacedAt": None
                })
                sensor_counter += 1

            # Additional sensors
            if random.random() > 0.5:
                # Soil moisture sensor
                sensor_id = f"SEN{sensor_counter:010d}"
                sensors.append({
                    "sensorId": sensor_id,
                    "type": "soil_moisture",
                    "subType": "TDR",
                    "fieldId": field["fieldId"],
                    "farmId": field["farmId"],
                    "location": {
                        "coordinates": [
                            farm["location"]["coordinates"][0] + random.uniform(-0.001, 0.001),
                            farm["location"]["coordinates"][1] + random.uniform(-0.001, 0.001)
                        ],
                        "height": -0.2,  # Below ground
                        "position": f"Field {field['name']} - Root Zone"
                    },
                    "manufacturer": "Decagon",
                    "model": "GS3",
                    "status": "active",
                    "specifications": {
                        "accuracy": random.uniform(93, 97),
                        "range": {"min": 0.0, "max": 100.0},
                        "measurementInterval": 30
                    },
                    "connectivity": {
                        "protocol": "LoRa",
                        "batteryLevel": random.randint(70, 100),
                        "lastCommunication": datetime.now() - timedelta(minutes=random.randint(0, 45)),
                        "signalStrength": random.randint(-80, -50)
                    },
                    "calibration": {
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(60, 180)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(90, 180)),
                        "offset": 0.0
                    },
                    "trapDetails": None,
                    "installedAt": field["plantingDate"],
                    "replacedAt": None
                })
                sensor_counter += 1

        # Insert sensors
        if sensors:
            result = self.db.sensors.insert_many(sensors)
            print(f"Seeded {len(result.inserted_ids)} sensors")

        return sensors

    def seed_initial_risk_assessments(self, fields):
        """Seed some recent risk assessments."""
        assessments = []
        assessment_counter = 1

        for field in fields[:10]:  # Last 10 fields
            # Create 2-3 recent assessments
            for i in range(random.randint(2, 3)):
                assessment_time = datetime.now() - timedelta(days=random.randint(1, 7))

                # Simulate risk factors
                leaf_wetness = random.uniform(0, 15)  # Scale 0-15
                temperature = random.uniform(15, 35)  # Celsius
                humidity = random.uniform(40, 95)  # Percentage
                rainfall_24h = random.uniform(0, 30)  # mm
                rainfall_72h = random.uniform(0, 60)  # mm
                trap_count = random.randint(0, 50)

                # Calculate risk score (simplified model)
                risk_score = 0.0
                explanation_parts = []

                # Leaf wetness contribution (0-30 points)
                if leaf_wetness > 10:
                    wetness_contrib = 30.0
                    explanation_parts.append("High leaf wetness (>10 hours) indicates severe disease risk")
                elif leaf_wetness > 6:
                    wetness_contrib = 20.0
                    explanation_parts.append("Moderate leaf wetness (6-10 hours) indicates moderate disease risk")
                elif leaf_wetness > 3:
                    wetness_contrib = 10.0
                    explanation_parts.append("Low leaf wetness (3-6 hours) indicates low disease risk")
                else:
                    wetness_contrib = 0.0
                    explanation_parts.append("Minimal leaf wetness (<3 hours) indicates very low disease risk")
                risk_score += wetness_contrib

                # Temperature contribution (0-20 points)
                if 20 <= temperature <= 28:
                    temp_contrib = 20.0
                    optimal = True
                    explanation_parts.append("Temperature in optimal range (20-28°C) for pathogen development")
                elif 15 <= temperature <= 32:
                    temp_contrib = 10.0
                    optimal = False
                    explanation_parts.append("Temperature in moderate range for pathogen development")
                else:
                    temp_contrib = 0.0
                    optimal = False
                    explanation_parts.append("Temperature outside favorable range for most pathogens")
                risk_score += temp_contrib

                # Humidity contribution (0-20 points)
                if humidity > 80:
                    humid_contrib = 20.0
                    explanation_parts.append("High humidity (>80%) favors disease development")
                elif humidity > 60:
                    humid_contrib = 10.0
                    explanation_parts.append("Moderate humidity (60-80%) provides some disease pressure")
                else:
                    humid_contrib = 0.0
                    explanation_parts.append("Low humidity (<60%) inhibits disease development")
                risk_score += humid_contrib

                # Rainfall contribution (0-15 points)
                if rainfall_24h > 15:
                    rain_contrib = 15.0
                    explanation_parts.append(f"Heavy rain ({rainfall_24h:.1f}mm in 24h) increases disease spread")
                elif rainfall_24h > 5:
                    rain_contrib = 8.0
                    explanation_parts.append(f"Moderate rain ({rainfall_24h:.1f}mm in 24h) may spread disease")
                else:
                    rain_contrib = 0.0
                    explanation_parts.append("Minimal rainfall reduces disease spread risk")
                risk_score += rain_contrib

                # Trap count contribution (0-15 points)
                threshold = 10  # Economic threshold
                if trap_count > threshold * 2:
                    trap_contrib = 15.0
                    trend = "increasing"
                    explanation_parts.append(f"High pest pressure ({trap_count} caught, 2x threshold)")
                elif trap_count > threshold:
                    trap_contrib = 8.0
                    trend = "stable"
                    explanation_parts.append(f"Moderate pest pressure ({trap_count} caught, above threshold)")
                else:
                    trap_contrib = 0.0
                    trend = "decreasing"
                    explanation_parts.append(f"Low pest pressure ({trap_count} caught, below threshold)")
                risk_score += trap_contrib

                # Determine risk level
                if risk_score >= 70:
                    risk_level = "critical"
                    action = "immediate_action"
                    priority = "urgent"
                elif risk_score >= 50:
                    risk_level = "high"
                    action = "curative_spray"
                    priority = "high"
                elif risk_score >= 30:
                    risk_level = "moderate"
                    action = "preventive_spray"
                    priority = "medium"
                else:
                    risk_level = "low"
                    action = "monitor_closely"
                    priority = "low"

                assessment = {
                    "assessmentId": f"RSK{assessment_counter:012d}",
                    "fieldId": field["fieldId"],
                    "farmId": field["farmId"],
                    "timestamp": assessment_time,
                    "riskScore": float(risk_score),
                    "riskLevel": risk_level,
                    "factors": {
                        "leafWetness": {
                            "value": leaf_wetness,
                            "weight": 0.30,
                            "contribution": float(wetness_contrib)
                        },
                        "temperature": {
                            "value": temperature,
                            "weight": 0.20,
                            "contribution": float(temp_contrib),
                            "optimal": optimal
                        },
                        "humidity": {
                            "value": humidity,
                            "weight": 0.20,
                            "contribution": float(humid_contrib)
                        },
                        "rainfall": {
                            "value": rainfall_24h,
                            "weight": 0.15,
                            "contribution": float(rain_contrib),
                            "recent24h": rainfall_24h,
                            "recent72h": rainfall_72h
                        },
                        "trapCount": {
                            "value": trap_count,  # Must be int per schema
                            "weight": 0.15,
                            "contribution": float(trap_contrib),
                            "trend": trend,
                            "threshold": threshold  # Must be int per schema
                        }
                    },
                    "diseases": [
                        {
                            "name": random.choice(field["riskHistory"]["commonDiseases"]),
                            "probability": risk_score * 0.8 + random.uniform(-10, 10),
                            "conditions_met": sum([wetness_contrib > 0, optimal, humid_contrib > 10]),
                            "total_conditions": 3
                        }
                    ],
                    "pests": [
                        {
                            "name": random.choice(field["riskHistory"]["commonPests"]),
                            "population": "high" if trap_count > threshold * 2 else "moderate" if trap_count > threshold else "low",
                            "trapCount": trap_count,
                            "economicThreshold": threshold
                        }
                    ],
                    "recommendation": {
                        "action": action,
                        "priority": priority,
                        "products": [
                            {
                                "name": random.choice(["Azoxystrobin", "Chlorothalonil", "Mancozeb"]),
                                "type": "fungicide",
                                "dosage": "2.5 L/ha",
                                "rei": 24,
                                "phi": 14
                            }
                        ] if action in ["preventive_spray", "curative_spray", "immediate_action"] else [],
                        "timing": "Within 24 hours" if priority == "urgent" else "Within 48 hours" if priority == "high" else "Within week",
                        "notes": f"Risk assessment based on current conditions. {' '.join(explanation_parts[:2])}"
                    },
                    "explanation": " ".join(explanation_parts),
                    "confidence": random.uniform(75, 95)
                }

                assessments.append(assessment)
                assessment_counter += 1

        # Insert assessments
        if assessments:
            result = self.db.risk_assessments.insert_many(assessments)
            print(f"Seeded {len(result.inserted_ids)} risk assessments")

        return assessments

    def seed_initial_events(self, fields, assessments):
        """Seed initial events based on risk assessments."""
        events = []
        event_counter = 1

        for assessment in assessments:
            # Generate event if risk is high enough
            if assessment["riskLevel"] in ["high", "critical"]:
                event_time = assessment["timestamp"] + timedelta(minutes=random.randint(5, 30))

                events.append({
                    "eventId": f"EVT{event_counter:012d}",
                    "eventType": "RISK_ALERT" if assessment["riskLevel"] == "high" else "SPRAY_RECOMMENDATION",
                    "fieldId": assessment["fieldId"],
                    "farmId": assessment["farmId"],
                    "timestamp": event_time,
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
                            "humidity": assessment["factors"]["humidity"]["value"]
                        },
                        "recommendedAction": assessment["recommendation"]["action"],
                        "economicImpact": random.uniform(1000, 10000) if assessment["riskLevel"] == "critical" else random.uniform(500, 2000)
                    },
                    "response": {
                        "action": "Spray applied" if random.random() > 0.3 else "Monitoring increased",
                        "timestamp": event_time + timedelta(hours=random.randint(1, 24)),
                        "implementedBy": "Farm Manager",
                        "result": "Successful" if random.random() > 0.2 else "Pending",
                        "notes": "Action taken based on risk assessment"
                    } if random.random() > 0.4 else None,
                    "acknowledged": random.choice([True, False]),
                    "acknowledgedBy": "farm_manager" if random.random() > 0.5 else None,
                    "acknowledgedAt": event_time + timedelta(minutes=random.randint(10, 120)) if random.random() > 0.5 else None,
                    "notifications": [
                        {
                            "method": random.choice(["sms", "email", "app"]),
                            "recipient": f"manager@farm{assessment['farmId'][-3:]}.com",
                            "sentAt": event_time,
                            "status": "delivered"
                        }
                    ] if assessment["riskLevel"] == "critical" else []
                })
                event_counter += 1

        # Insert events
        if events:
            result = self.db.events.insert_many(events)
            print(f"Seeded {len(result.inserted_ids)} initial events")

        return events

    def run(self, clean=False):
        """Run the complete seeding process."""
        print("\n" + "="*50)
        print("Agricultural Pest & Disease Risk Scoring - Data Seeding")
        print("="*50)

        if clean:
            print("\nCleaning existing data...")
            self.clean_collections()

        print("\nSeeding infrastructure data...")

        # Seed farms
        farms = self.seed_farms()

        # Seed fields
        fields = self.seed_fields(farms)

        # Seed sensors
        sensors = self.seed_sensors(fields, farms)

        # Seed initial risk assessments
        assessments = self.seed_initial_risk_assessments(fields)

        # Seed initial events
        events = self.seed_initial_events(fields, assessments)

        print("\n" + "="*50)
        print("Seeding complete!")
        print(f"Database: {self.db.name}")
        print(f"Farms: {len(farms)}")
        print(f"Fields: {len(fields)}")
        print(f"Sensors: {len(sensors)}")
        print(f"Risk Assessments: {len(assessments)}")
        print(f"Events: {len(events)}")
        print("="*50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed agricultural monitoring data")
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
    seeder = AgriculturalSeeder(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    seeder.run(clean=args.clean)


if __name__ == "__main__":
    main()