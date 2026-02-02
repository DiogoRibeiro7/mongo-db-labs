#!/usr/bin/env python3
"""
Smart Grid Energy Monitoring - Infrastructure Seeding Script
Seeds buildings, smart meters, and tariff plans
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB connection settings
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "energygrid_db"


class EnergyGridSeeder:
    """Seeds energy grid infrastructure data."""

    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, seed=None):
        """Initialize seeder with MongoDB connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        if seed is not None:
            random.seed(seed)
            print(f"Using random seed: {seed}")

    def clean_collections(self):
        """Remove existing data from all collections."""
        collections = ["buildings", "meters", "tariffs", "events", "bills"]
        for coll in collections:
            count = self.db[coll].delete_many({}).deleted_count
            if count > 0:
                print(f"Cleaned {count} documents from {coll}")

    def seed_tariffs(self):
        """Seed tariff plans."""
        tariffs = []

        # Residential tariffs
        tariffs.append({
            "tariffId": "TAR0001",
            "name": "Residential Standard",
            "type": "flat",
            "customerType": "residential",
            "description": "Standard flat rate for residential customers",
            "validFrom": datetime.now() - timedelta(days=365),
            "validUntil": None,
            "rates": {
                "currency": "USD",
                "flatRate": {
                    "pricePerKWh": 0.12
                },
                "fixedCharges": {
                    "monthlyCharge": 10.00,
                    "connectionCharge": 0.00,
                    "demandCharge": None
                },
                "taxes": [
                    {"name": "State Tax", "rate": 0.05, "fixedAmount": None},
                    {"name": "City Tax", "rate": 0.02, "fixedAmount": None}
                ]
            },
            "incentives": {
                "solarFeedIn": 0.08,
                "evCharging": 0.10,
                "greenEnergy": 0.00
            },
            "penalties": {
                "latePayment": 0.015
            }
        })

        tariffs.append({
            "tariffId": "TAR0002",
            "name": "Residential Time-of-Use",
            "type": "time_of_use",
            "customerType": "residential",
            "description": "Time-of-use rates with peak and off-peak pricing",
            "validFrom": datetime.now() - timedelta(days=365),
            "validUntil": None,
            "rates": {
                "currency": "USD",
                "timeOfUse": {
                    "peak": {
                        "hours": [
                            {"start": "16:00", "end": "21:00"}
                        ],
                        "pricePerKWh": 0.20
                    },
                    "offPeak": {
                        "pricePerKWh": 0.08
                    },
                    "shoulder": {
                        "hours": [
                            {"start": "07:00", "end": "16:00"},
                            {"start": "21:00", "end": "23:00"}
                        ],
                        "pricePerKWh": 0.12
                    }
                },
                "fixedCharges": {
                    "monthlyCharge": 12.00,
                    "connectionCharge": 0.00,
                    "demandCharge": None
                },
                "taxes": [
                    {"name": "State Tax", "rate": 0.05, "fixedAmount": None},
                    {"name": "City Tax", "rate": 0.02, "fixedAmount": None}
                ]
            },
            "incentives": {
                "solarFeedIn": 0.10,
                "evCharging": 0.06,
                "greenEnergy": 0.01
            },
            "penalties": {
                "latePayment": 0.015
            }
        })

        tariffs.append({
            "tariffId": "TAR0003",
            "name": "Residential Tiered",
            "type": "tiered",
            "customerType": "residential",
            "description": "Tiered pricing based on consumption",
            "validFrom": datetime.now() - timedelta(days=365),
            "validUntil": None,
            "rates": {
                "currency": "USD",
                "tiers": [
                    {"minKWh": 0, "maxKWh": 500, "pricePerKWh": 0.10},
                    {"minKWh": 500, "maxKWh": 1000, "pricePerKWh": 0.12},
                    {"minKWh": 1000, "maxKWh": None, "pricePerKWh": 0.15}
                ],
                "fixedCharges": {
                    "monthlyCharge": 8.00,
                    "connectionCharge": 0.00,
                    "demandCharge": None
                },
                "taxes": [
                    {"name": "State Tax", "rate": 0.05, "fixedAmount": None},
                    {"name": "City Tax", "rate": 0.02, "fixedAmount": None}
                ]
            },
            "incentives": {
                "solarFeedIn": 0.08,
                "evCharging": 0.08,
                "greenEnergy": 0.00
            },
            "penalties": {
                "latePayment": 0.015
            }
        })

        # Commercial tariffs
        tariffs.append({
            "tariffId": "TAR1001",
            "name": "Commercial Standard",
            "type": "time_of_use",
            "customerType": "commercial",
            "description": "Standard commercial time-of-use with demand charges",
            "validFrom": datetime.now() - timedelta(days=365),
            "validUntil": None,
            "rates": {
                "currency": "USD",
                "timeOfUse": {
                    "peak": {
                        "hours": [
                            {"start": "09:00", "end": "17:00"}
                        ],
                        "pricePerKWh": 0.18
                    },
                    "offPeak": {
                        "pricePerKWh": 0.09
                    }
                },
                "fixedCharges": {
                    "monthlyCharge": 50.00,
                    "connectionCharge": 0.00,
                    "demandCharge": 15.00  # per kW
                },
                "taxes": [
                    {"name": "State Tax", "rate": 0.05, "fixedAmount": None},
                    {"name": "Commercial Tax", "rate": 0.03, "fixedAmount": None}
                ]
            },
            "incentives": {
                "solarFeedIn": 0.12,
                "evCharging": 0.08,
                "greenEnergy": 0.02
            },
            "penalties": {
                "exceededDemand": 25.00,
                "powerFactor": 0.05,
                "latePayment": 0.02
            }
        })

        # Industrial tariffs
        tariffs.append({
            "tariffId": "TAR2001",
            "name": "Industrial High Voltage",
            "type": "time_of_use",
            "customerType": "industrial",
            "description": "Industrial high voltage with demand and power factor charges",
            "validFrom": datetime.now() - timedelta(days=365),
            "validUntil": None,
            "rates": {
                "currency": "USD",
                "timeOfUse": {
                    "peak": {
                        "hours": [
                            {"start": "06:00", "end": "22:00"}
                        ],
                        "pricePerKWh": 0.14
                    },
                    "offPeak": {
                        "pricePerKWh": 0.07
                    }
                },
                "fixedCharges": {
                    "monthlyCharge": 200.00,
                    "connectionCharge": 0.00,
                    "demandCharge": 12.00  # per kW
                },
                "taxes": [
                    {"name": "State Tax", "rate": 0.05, "fixedAmount": None},
                    {"name": "Industrial Tax", "rate": 0.02, "fixedAmount": None}
                ]
            },
            "incentives": {
                "solarFeedIn": 0.15,
                "evCharging": 0.10,
                "greenEnergy": 0.03
            },
            "penalties": {
                "exceededDemand": 30.00,
                "powerFactor": 0.08,
                "latePayment": 0.025
            }
        })

        # Insert tariffs
        if tariffs:
            result = self.db.tariffs.insert_many(tariffs)
            print(f"Seeded {len(result.inserted_ids)} tariff plans")

        return tariffs

    def seed_buildings(self, tariffs):
        """Seed buildings of different types."""
        buildings = []
        building_counter = 1

        # Residential buildings
        residential_types = [
            ("single_family", "House", 1, 1, 150, 2),
            ("apartment", "Apartment Complex", 4, 24, 2000, 50),
            ("condo", "Condo Building", 10, 40, 4000, 80)
        ]

        for subtype, name_prefix, floors, units, sqm, residents in residential_types:
            for i in range(random.randint(2, 4)):
                building_id = f"BLD{building_counter:08d}"
                buildings.append({
                    "buildingId": building_id,
                    "type": "residential",
                    "subType": subtype,
                    "name": f"{name_prefix} {building_id[-3:]}",
                    "address": {
                        "street": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Park', 'First'])} Street",
                        "city": random.choice(["San Francisco", "Los Angeles", "San Diego"]),
                        "state": "CA",
                        "postalCode": f"9{random.randint(1000, 9999)}",
                        "country": "USA",
                        "coordinates": {
                            "lat": 37.7749 + random.uniform(-0.1, 0.1),
                            "lng": -122.4194 + random.uniform(-0.1, 0.1)
                        }
                    },
                    "status": "active",
                    "characteristics": {
                        "floors": floors,
                        "units": units,
                        "squareMeters": sqm * (1 + random.uniform(-0.2, 0.3)),
                        "yearBuilt": random.randint(1960, 2023),
                        "energyClass": random.choice(["A", "B", "B", "C", "C", "D"]),
                        "hasSolar": random.choice([True, False, False]),
                        "hasBackupPower": subtype != "single_family",
                        "hasEVCharging": random.choice([True, False])
                    },
                    "occupancy": {
                        "residents": residents + random.randint(-5, 10),
                        "businesses": 0,
                        "typicalOccupancy": {
                            "weekday": int(residents * 0.7),
                            "weekend": residents
                        }
                    },
                    "contractInfo": {
                        "accountNumber": f"ACC{random.randint(100000, 999999)}",
                        "tariffPlanId": random.choice(["TAR0001", "TAR0002", "TAR0003"]),
                        "contractStart": datetime.now() - timedelta(days=random.randint(30, 1000)),
                        "contractEnd": None,
                        "maxDemandKW": units * random.uniform(3, 5),
                        "voltageLevel": "LV"
                    },
                    "createdAt": datetime.now() - timedelta(days=random.randint(365, 1825)),
                    "updatedAt": None
                })
                building_counter += 1

        # Commercial buildings
        commercial_types = [
            ("office", "Office Building", 10, 50, 5000, 0, 500),
            ("retail", "Shopping Center", 2, 20, 3000, 0, 200),
            ("hospital", "Medical Center", 8, 1, 10000, 50, 1000),
            ("school", "School", 3, 1, 4000, 0, 800)
        ]

        for subtype, name_prefix, floors, units, sqm, residents, occupants in commercial_types:
            for i in range(random.randint(1, 2)):
                building_id = f"BLD{building_counter:08d}"
                buildings.append({
                    "buildingId": building_id,
                    "type": "commercial",
                    "subType": subtype,
                    "name": f"{name_prefix} {building_id[-3:]}",
                    "address": {
                        "street": f"{random.randint(1, 99)} {random.choice(['Business', 'Commerce', 'Industrial', 'Tech'])} Blvd",
                        "city": random.choice(["San Francisco", "Los Angeles", "San Jose"]),
                        "state": "CA",
                        "postalCode": f"9{random.randint(1000, 9999)}",
                        "country": "USA",
                        "coordinates": {
                            "lat": 37.7749 + random.uniform(-0.2, 0.2),
                            "lng": -122.4194 + random.uniform(-0.2, 0.2)
                        }
                    },
                    "status": "active",
                    "characteristics": {
                        "floors": floors,
                        "units": units,
                        "squareMeters": sqm * (1 + random.uniform(-0.1, 0.2)),
                        "yearBuilt": random.randint(1980, 2023),
                        "energyClass": random.choice(["A", "B", "C", "C", "D"]),
                        "hasSolar": random.choice([True, True, False]),
                        "hasBackupPower": True,
                        "hasEVCharging": True
                    },
                    "occupancy": {
                        "residents": residents,
                        "businesses": units,
                        "typicalOccupancy": {
                            "weekday": occupants,
                            "weekend": int(occupants * 0.2)
                        }
                    },
                    "contractInfo": {
                        "accountNumber": f"ACC{random.randint(100000, 999999)}",
                        "tariffPlanId": "TAR1001",
                        "contractStart": datetime.now() - timedelta(days=random.randint(180, 2000)),
                        "contractEnd": datetime.now() + timedelta(days=random.randint(180, 730)),
                        "maxDemandKW": sqm * 0.05,
                        "voltageLevel": "MV"
                    },
                    "createdAt": datetime.now() - timedelta(days=random.randint(730, 3650)),
                    "updatedAt": datetime.now() - timedelta(days=random.randint(1, 30))
                })
                building_counter += 1

        # Industrial buildings
        industrial_types = [
            ("factory", "Manufacturing Plant", 2, 1, 8000, 0, 200),
            ("warehouse", "Distribution Center", 1, 1, 10000, 0, 50),
            ("data_center", "Data Center", 3, 1, 5000, 0, 20)
        ]

        for subtype, name_prefix, floors, units, sqm, residents, occupants in industrial_types:
            building_id = f"BLD{building_counter:08d}"
            buildings.append({
                "buildingId": building_id,
                "type": "industrial",
                "subType": subtype,
                "name": f"{name_prefix} {building_id[-3:]}",
                "address": {
                    "street": f"{random.randint(1, 999)} Industrial Way",
                    "city": random.choice(["Oakland", "Richmond", "Fremont"]),
                    "state": "CA",
                    "postalCode": f"9{random.randint(1000, 9999)}",
                    "country": "USA",
                    "coordinates": {
                        "lat": 37.8044 + random.uniform(-0.1, 0.1),
                        "lng": -122.2712 + random.uniform(-0.1, 0.1)
                    }
                },
                "status": "active",
                "characteristics": {
                    "floors": floors,
                    "units": units,
                    "squareMeters": sqm * (1 + random.uniform(0, 0.5)),
                    "yearBuilt": random.randint(1970, 2020),
                    "energyClass": random.choice(["B", "C", "D", "E"]),
                    "hasSolar": subtype == "warehouse",
                    "hasBackupPower": True,
                    "hasEVCharging": random.choice([True, False])
                },
                "occupancy": {
                    "residents": residents,
                    "businesses": 1,
                    "typicalOccupancy": {
                        "weekday": occupants,
                        "weekend": int(occupants * 0.3) if subtype != "data_center" else occupants
                    }
                },
                "contractInfo": {
                    "accountNumber": f"ACC{random.randint(100000, 999999)}",
                    "tariffPlanId": "TAR2001",
                    "contractStart": datetime.now() - timedelta(days=random.randint(365, 3650)),
                    "contractEnd": datetime.now() + timedelta(days=random.randint(365, 1095)),
                    "maxDemandKW": sqm * 0.1 if subtype == "data_center" else sqm * 0.03,
                    "voltageLevel": "HV"
                },
                "createdAt": datetime.now() - timedelta(days=random.randint(1095, 5475)),
                "updatedAt": datetime.now() - timedelta(days=random.randint(1, 60))
            })
            building_counter += 1

        # Insert buildings
        if buildings:
            result = self.db.buildings.insert_many(buildings)
            print(f"Seeded {len(result.inserted_ids)} buildings")

        return buildings

    def seed_meters(self, buildings):
        """Seed smart meters for buildings."""
        meters = []
        meter_counter = 1

        for building in buildings:
            # Number of meters depends on building type
            if building["subType"] == "single_family":
                num_meters = 1
            elif building["subType"] in ["apartment", "condo"]:
                num_meters = building["characteristics"]["units"] + 1  # Plus common area
            elif building["type"] == "commercial":
                num_meters = random.randint(1, 3)
            else:  # Industrial
                num_meters = random.randint(2, 5)

            for i in range(num_meters):
                meter_id = f"MTR{meter_counter:010d}"

                # Determine meter configuration
                if building["contractInfo"]["voltageLevel"] == "HV":
                    meter_subtype = "three_phase"
                elif building["type"] == "commercial" or building["type"] == "industrial":
                    meter_subtype = "three_phase"
                else:
                    meter_subtype = random.choice(["single_phase", "single_phase", "three_phase"])

                # Solar meters for buildings with solar
                if i == 1 and building["characteristics"].get("hasSolar"):
                    meter_type = "solar"
                    meter_subtype = "net_metering"
                else:
                    meter_type = "electricity"

                meters.append({
                    "meterId": meter_id,
                    "buildingId": building["buildingId"],
                    "type": meter_type,
                    "subType": meter_subtype,
                    "manufacturer": random.choice(["Landis+Gyr", "Itron", "Schneider", "Siemens", "GE"]),
                    "model": f"SM-{random.choice(['X', 'Z', 'Q'])}{random.randint(1000, 9999)}",
                    "status": random.choices(
                        ["active", "inactive", "maintenance"],
                        weights=[0.95, 0.03, 0.02]
                    )[0],
                    "capabilities": {
                        "bidirectional": meter_type == "solar",
                        "remoteDisconnect": building["type"] != "industrial",
                        "powerQuality": meter_subtype == "three_phase",
                        "tamperDetection": True,
                        "realtimeData": True
                    },
                    "specifications": {
                        "maxCurrent": 200.0 if meter_subtype == "three_phase" else 100.0,
                        "maxVoltage": 480.0 if building["contractInfo"]["voltageLevel"] == "HV" else 240.0,
                        "accuracy": random.uniform(98.5, 99.9),
                        "measurementInterval": random.choice([15, 30, 60])
                    },
                    "connectivity": {
                        "protocol": random.choice(["cellular", "plc", "zigbee", "lorawan"]),
                        "lastCommunication": datetime.now() - timedelta(minutes=random.randint(0, 120)),
                        "signalStrength": random.randint(-80, -40),
                        "firmwareVersion": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}"
                    },
                    "location": {
                        "floor": 0 if building["characteristics"]["floors"] == 1 else random.randint(-1, 1),
                        "unit": f"Unit-{i+1}" if building["characteristics"]["units"] > 1 else None,
                        "position": random.choice(["basement", "utility_room", "exterior", "roof"]) if i == 0 else "unit",
                        "coordinates": None
                    },
                    "calibration": {
                        "lastCalibrated": datetime.now() - timedelta(days=random.randint(30, 365)),
                        "nextCalibration": datetime.now() + timedelta(days=random.randint(180, 730)),
                        "calibrationFactor": 1.0 + random.uniform(-0.002, 0.002)
                    },
                    "installedAt": building["createdAt"] + timedelta(days=random.randint(1, 30)),
                    "replacedAt": None
                })
                meter_counter += 1

        # Insert meters
        if meters:
            result = self.db.meters.insert_many(meters)
            print(f"Seeded {len(result.inserted_ids)} smart meters")

        return meters

    def seed_initial_events(self, buildings, meters):
        """Seed some initial events."""
        events = []
        event_counter = 1

        # Recent events for some buildings
        for building in random.sample(buildings, min(10, len(buildings))):
            building_meters = [m for m in meters if m["buildingId"] == building["buildingId"]]

            # Peak demand event
            if building["type"] in ["commercial", "industrial"]:
                event_time = datetime.now() - timedelta(hours=random.randint(1, 72))
                events.append({
                    "eventId": f"EVT{event_counter:012d}",
                    "eventType": "peak_demand",
                    "meterId": random.choice(building_meters)["meterId"] if building_meters else None,
                    "buildingId": building["buildingId"],
                    "timestamp": event_time,
                    "endTime": event_time + timedelta(minutes=random.randint(15, 120)),
                    "severity": random.choice(["warning", "critical"]),
                    "details": {
                        "peakValue": building["contractInfo"]["maxDemandKW"] * random.uniform(1.05, 1.3),
                        "thresholdExceeded": building["contractInfo"]["maxDemandKW"],
                        "estimatedCost": random.uniform(50, 500)
                    },
                    "location": {
                        "grid": f"Grid-{random.randint(1, 5)}",
                        "substation": f"SUB-{random.randint(100, 999)}",
                        "feeder": f"FDR-{random.randint(1, 20)}"
                    },
                    "response": {
                        "automated": True,
                        "action": "Load shedding initiated",
                        "timestamp": event_time + timedelta(minutes=random.randint(1, 5)),
                        "result": "Peak demand reduced"
                    },
                    "acknowledged": True,
                    "acknowledgedBy": "system",
                    "acknowledgedAt": event_time + timedelta(minutes=random.randint(5, 30))
                })
                event_counter += 1

            # Voltage issues
            if random.random() > 0.7:
                event_time = datetime.now() - timedelta(hours=random.randint(24, 168))
                events.append({
                    "eventId": f"EVT{event_counter:012d}",
                    "eventType": random.choice(["voltage_sag", "voltage_spike"]),
                    "meterId": random.choice(building_meters)["meterId"] if building_meters else None,
                    "buildingId": building["buildingId"],
                    "timestamp": event_time,
                    "endTime": event_time + timedelta(seconds=random.randint(1, 300)),
                    "severity": "warning",
                    "details": {
                        "duration": random.randint(1, 300),
                        "affectedUnits": random.randint(1, building["characteristics"]["units"]),
                        "peakValue": random.uniform(200, 260) if random.random() > 0.5 else random.uniform(100, 200)
                    },
                    "location": {
                        "grid": f"Grid-{random.randint(1, 5)}",
                        "substation": f"SUB-{random.randint(100, 999)}",
                        "feeder": f"FDR-{random.randint(1, 20)}"
                    },
                    "response": None,
                    "acknowledged": random.choice([True, False]),
                    "acknowledgedBy": "operator" if random.random() > 0.5 else None,
                    "acknowledgedAt": event_time + timedelta(minutes=random.randint(10, 60)) if random.random() > 0.5 else None
                })
                event_counter += 1

        # Insert events
        if events:
            result = self.db.events.insert_many(events)
            print(f"Seeded {len(result.inserted_ids)} initial events")

        return events

    def seed_initial_bills(self, buildings, tariffs):
        """Seed recent bills for buildings."""
        bills = []
        bill_counter = 1

        # Create last month's bill for each building
        for building in buildings:
            # Get the tariff for this building
            tariff = next((t for t in tariffs if t["tariffId"] == building["contractInfo"]["tariffPlanId"]), None)
            if not tariff:
                continue

            # Billing period (last month)
            end_date = datetime.now().replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
            days = (end_date - start_date).days + 1

            # Calculate consumption based on building type
            base_consumption = {
                "single_family": 900,
                "apartment": 600,
                "condo": 700,
                "office": 5000,
                "retail": 3000,
                "hospital": 20000,
                "school": 8000,
                "factory": 15000,
                "warehouse": 5000,
                "data_center": 50000
            }.get(building.get("subType"), 1000)

            # Add variation
            total_kwh = base_consumption * random.uniform(0.8, 1.2)

            # Time-of-use breakdown
            if tariff["type"] == "time_of_use":
                peak_kwh = total_kwh * 0.35
                off_peak_kwh = total_kwh * 0.45
                shoulder_kwh = total_kwh * 0.20
            else:
                peak_kwh = 0
                off_peak_kwh = 0
                shoulder_kwh = 0

            # Calculate charges
            if tariff["type"] == "flat":
                energy_charge = total_kwh * tariff["rates"]["flatRate"]["pricePerKWh"]
            elif tariff["type"] == "time_of_use":
                tou = tariff["rates"]["timeOfUse"]
                energy_charge = (
                    peak_kwh * tou["peak"]["pricePerKWh"] +
                    off_peak_kwh * tou["offPeak"]["pricePerKWh"]
                )
                if tou.get("shoulder"):
                    energy_charge += shoulder_kwh * tou["shoulder"]["pricePerKWh"]
            elif tariff["type"] == "tiered":
                energy_charge = 0
                remaining = total_kwh
                for tier in tariff["rates"]["tiers"]:
                    if remaining <= 0:
                        break
                    tier_usage = min(remaining, (tier["maxKWh"] or float('inf')) - tier["minKWh"])
                    energy_charge += tier_usage * tier["pricePerKWh"]
                    remaining -= tier_usage
            else:
                energy_charge = total_kwh * 0.12  # Default

            # Add fixed charges
            fixed_charges = tariff["rates"]["fixedCharges"]
            fixed_charge = fixed_charges.get("monthlyCharge", 0)

            # Demand charge for commercial/industrial
            demand_charge = 0
            peak_demand_kw = 0
            if building["type"] in ["commercial", "industrial"]:
                peak_demand_kw = building["contractInfo"]["maxDemandKW"] * random.uniform(0.6, 0.95)
                demand_charge = peak_demand_kw * fixed_charges.get("demandCharge", 0)

            # Calculate taxes
            subtotal = energy_charge + fixed_charge + demand_charge
            taxes = sum(subtotal * tax["rate"] for tax in tariff["rates"].get("taxes", []))

            # Total amount
            total_amount = subtotal + taxes

            bills.append({
                "billId": f"BILL{bill_counter:010d}",
                "buildingId": building["buildingId"],
                "accountNumber": building["contractInfo"]["accountNumber"],
                "billingPeriod": {
                    "start": start_date,
                    "end": end_date,
                    "days": days
                },
                "consumption": {
                    "totalKWh": round(total_kwh, 2),
                    "peakKWh": round(peak_kwh, 2),
                    "offPeakKWh": round(off_peak_kwh, 2),
                    "shoulderKWh": round(shoulder_kwh, 2) if shoulder_kwh > 0 else None,
                    "peakDemandKW": round(peak_demand_kw, 2),
                    "averageDailyKWh": round(total_kwh / days, 2),
                    "powerFactor": random.uniform(0.85, 0.99)
                },
                "charges": {
                    "energyCharge": round(energy_charge, 2),
                    "demandCharge": round(demand_charge, 2) if demand_charge > 0 else None,
                    "fixedCharge": round(fixed_charge, 2),
                    "taxes": round(taxes, 2),
                    "adjustments": None,
                    "credits": None,
                    "total": round(total_amount, 2)
                },
                "tariffApplied": {
                    "tariffId": tariff["tariffId"],
                    "name": tariff["name"],
                    "rates": {
                        "peak": tariff["rates"]["timeOfUse"]["peak"]["pricePerKWh"] if tariff["type"] == "time_of_use" else None,
                        "offPeak": tariff["rates"]["timeOfUse"]["offPeak"]["pricePerKWh"] if tariff["type"] == "time_of_use" else None,
                        "flat": tariff["rates"]["flatRate"]["pricePerKWh"] if tariff["type"] == "flat" else None
                    }
                },
                "comparison": {
                    "previousMonth": round(total_amount * random.uniform(0.85, 1.15), 2),
                    "previousYear": round(total_amount * random.uniform(0.90, 1.10), 2),
                    "percentChange": round(random.uniform(-15, 15), 1)
                },
                "status": random.choices(
                    ["paid", "issued", "overdue"],
                    weights=[0.7, 0.2, 0.1]
                )[0],
                "totalAmount": round(total_amount, 2),
                "currency": tariff["rates"]["currency"],
                "dueDate": end_date + timedelta(days=20),
                "issuedAt": end_date + timedelta(days=3),
                "paidAt": end_date + timedelta(days=random.randint(5, 18)) if random.random() > 0.3 else None,
                "paymentMethod": random.choice(["credit_card", "bank_transfer", "direct_debit"]) if random.random() > 0.3 else None,
                "createdAt": end_date + timedelta(days=3),
                "updatedAt": None
            })
            bill_counter += 1

        # Insert bills
        if bills:
            result = self.db.bills.insert_many(bills)
            print(f"Seeded {len(result.inserted_ids)} bills")

        return bills

    def run(self, clean=False):
        """Run the complete seeding process."""
        print("\n" + "="*50)
        print("Smart Grid Energy Monitoring - Infrastructure Seeding")
        print("="*50)

        if clean:
            print("\nCleaning existing data...")
            self.clean_collections()

        print("\nSeeding infrastructure data...")

        # Seed tariffs first
        tariffs = self.seed_tariffs()

        # Seed buildings
        buildings = self.seed_buildings(tariffs)

        # Seed meters
        meters = self.seed_meters(buildings)

        # Seed initial events
        events = self.seed_initial_events(buildings, meters)

        # Seed initial bills
        bills = self.seed_initial_bills(buildings, tariffs)

        print("\n" + "="*50)
        print("Seeding complete!")
        print(f"Database: {self.db.name}")
        print(f"Tariff plans: {len(tariffs)}")
        print(f"Buildings: {len(buildings)}")
        print(f"Smart meters: {len(meters)}")
        print(f"Events: {len(events)}")
        print(f"Bills: {len(bills)}")
        print("="*50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed energy grid infrastructure data")
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
    seeder = EnergyGridSeeder(mongo_uri=mongo_uri, db_name=db_name, seed=args.seed)
    seeder.run(clean=args.clean)


if __name__ == "__main__":
    main()