// =====================================================
// Smart Parking Occupancy - MongoDB Setup
// Database: smartparking_db
// Purpose: Smart city parking management system
// =====================================================

// Use the database
const dbName = "smartparking_db";
const db = db.getSiblingDB(dbName);

print(`\nSetting up database: ${dbName}`);
print("=" + "=".repeat(50));

// Drop existing collections for clean setup
const collections = ["zones", "parking_spots", "sensors", "occupancy_readings", "events", "violations"];
collections.forEach(coll => {
    try {
        db[coll].drop();
        print(`Dropped collection: ${coll}`);
    } catch (e) {
        // Collection doesn't exist, ignore
    }
});

// =====================================================
// Create Collections
// =====================================================

// 1. Zones collection (parking areas/districts)
db.createCollection("zones", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["zoneId", "name", "type", "location", "totalSpots", "pricing", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                zoneId: {
                    bsonType: "string",
                    pattern: "^ZONE[0-9]{4}$",
                    description: "Zone identifier"
                },
                name: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 100
                },
                type: {
                    enum: ["street", "garage", "lot", "underground", "rooftop"],
                    description: "Type of parking zone"
                },
                location: {
                    bsonType: "object",
                    required: ["type", "coordinates", "address"],
                    additionalProperties: false,
                    properties: {
                        type: { enum: ["Polygon"] },
                        coordinates: {
                            bsonType: "array",
                            description: "GeoJSON polygon coordinates"
                        },
                        address: {
                            bsonType: "string",
                            maxLength: 200
                        },
                        city: { bsonType: "string" },
                        district: { bsonType: "string" }
                    }
                },
                totalSpots: {
                    bsonType: "int",
                    minimum: 1,
                    maximum: 10000
                },
                reservedSpots: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        disabled: { bsonType: "int", minimum: 0 },
                        electric: { bsonType: "int", minimum: 0 },
                        vip: { bsonType: "int", minimum: 0 },
                        loading: { bsonType: "int", minimum: 0 }
                    }
                },
                pricing: {
                    bsonType: "object",
                    required: ["currency", "perHour"],
                    additionalProperties: false,
                    properties: {
                        currency: { enum: ["USD", "EUR", "GBP"] },
                        perHour: { bsonType: "double", minimum: 0 },
                        perDay: { bsonType: ["double", "null"], minimum: 0 },
                        freeMinutes: { bsonType: "int", minimum: 0 },
                        maxDailyCharge: { bsonType: ["double", "null"] },
                        peakHourMultiplier: { bsonType: "double", minimum: 1.0 }
                    }
                },
                regulations: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        maxStayHours: { bsonType: ["int", "null"], minimum: 1 },
                        operatingHours: {
                            bsonType: "object",
                            properties: {
                                start: { bsonType: "string", pattern: "^[0-2][0-9]:[0-5][0-9]$" },
                                end: { bsonType: "string", pattern: "^[0-2][0-9]:[0-5][0-9]$" }
                            }
                        },
                        permitRequired: { bsonType: "bool" },
                        restrictions: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        }
                    }
                },
                features: {
                    bsonType: "array",
                    items: {
                        enum: ["covered", "surveillance", "lighting", "ev_charging", "valet", "payment_app"]
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 2. Parking Spots collection
db.createCollection("parking_spots", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["spotId", "zoneId", "spotNumber", "type", "status", "location", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                spotId: {
                    bsonType: "string",
                    pattern: "^SPOT[0-9]{8}$",
                    description: "Unique spot identifier"
                },
                zoneId: {
                    bsonType: "string",
                    pattern: "^ZONE[0-9]{4}$"
                },
                spotNumber: {
                    bsonType: "string",
                    description: "Display number (e.g., 'A-101', 'B2-45')"
                },
                type: {
                    enum: ["standard", "compact", "disabled", "electric", "motorcycle", "loading", "vip"],
                    description: "Type of parking spot"
                },
                status: {
                    enum: ["available", "occupied", "reserved", "maintenance", "violation"],
                    description: "Current spot status"
                },
                location: {
                    bsonType: "object",
                    required: ["type", "coordinates"],
                    properties: {
                        type: { enum: ["Point"] },
                        coordinates: {
                            bsonType: "array",
                            minItems: 2,
                            maxItems: 2,
                            items: [
                                { bsonType: "double", minimum: -180, maximum: 180 },
                                { bsonType: "double", minimum: -90, maximum: 90 }
                            ]
                        },
                        level: { bsonType: ["int", "null"] },
                        section: { bsonType: ["string", "null"] }
                    }
                },
                dimensions: {
                    bsonType: "object",
                    properties: {
                        length: { bsonType: "double", minimum: 0 },
                        width: { bsonType: "double", minimum: 0 },
                        unit: { enum: ["meters", "feet"] }
                    }
                },
                currentOccupant: {
                    bsonType: ["object", "null"],
                    properties: {
                        vehicleId: { bsonType: "string" },
                        licensePlate: { bsonType: "string" },
                        entryTime: { bsonType: "date" },
                        paymentMethod: { enum: ["app", "meter", "permit", "free"] },
                        paidUntil: { bsonType: ["date", "null"] }
                    }
                },
                sensorId: {
                    bsonType: ["string", "null"],
                    pattern: "^SEN[0-9]{8}$"
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 3. Sensors collection
db.createCollection("sensors", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["sensorId", "type", "spotId", "status", "installedAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                sensorId: {
                    bsonType: "string",
                    pattern: "^SEN[0-9]{8}$"
                },
                type: {
                    enum: ["magnetometer", "ultrasonic", "infrared", "camera", "radar"],
                    description: "Sensor technology type"
                },
                model: {
                    bsonType: "string",
                    maxLength: 50
                },
                spotId: {
                    bsonType: ["string", "null"],
                    pattern: "^SPOT[0-9]{8}$"
                },
                zoneId: {
                    bsonType: ["string", "null"],
                    pattern: "^ZONE[0-9]{4}$"
                },
                status: {
                    enum: ["active", "inactive", "faulty", "maintenance", "offline"],
                    description: "Sensor operational status"
                },
                connectivity: {
                    bsonType: "object",
                    properties: {
                        protocol: { enum: ["LoRa", "NB-IoT", "WiFi", "Zigbee", "4G"] },
                        gatewayId: { bsonType: "string" },
                        signalStrength: { bsonType: "int", minimum: -120, maximum: 0 },
                        lastSeen: { bsonType: "date" }
                    }
                },
                calibration: {
                    bsonType: "object",
                    properties: {
                        baseline: { bsonType: "double" },
                        threshold: { bsonType: "double" },
                        sensitivity: { bsonType: "int", minimum: 1, maximum: 10 },
                        lastCalibrated: { bsonType: "date" }
                    }
                },
                batteryLevel: {
                    bsonType: ["int", "null"],
                    minimum: 0,
                    maximum: 100
                },
                firmware: {
                    bsonType: "object",
                    properties: {
                        version: { bsonType: "string" },
                        lastUpdate: { bsonType: "date" }
                    }
                },
                installedAt: { bsonType: "date" },
                lastReading: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 4. Occupancy Readings collection (time-series)
// Note: Time-series collections don't support validators
db.createCollection("occupancy_readings", {
    timeseries: {
        timeField: "timestamp",
        metaField: "meta",
        granularity: "seconds"
    }
});

// 5. Events collection
db.createCollection("events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["eventId", "eventType", "timestamp", "spotId"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                eventId: {
                    bsonType: "string",
                    pattern: "^EVT[0-9]{10}$"
                },
                eventType: {
                    enum: [
                        "occupancy_change",
                        "overstay_warning",
                        "overstay_violation",
                        "payment_expired",
                        "sensor_offline",
                        "sensor_fault",
                        "illegal_parking",
                        "reservation_start",
                        "reservation_end"
                    ]
                },
                spotId: {
                    bsonType: "string",
                    pattern: "^SPOT[0-9]{8}$"
                },
                zoneId: {
                    bsonType: "string",
                    pattern: "^ZONE[0-9]{4}$"
                },
                sensorId: {
                    bsonType: ["string", "null"],
                    pattern: "^SEN[0-9]{8}$"
                },
                timestamp: { bsonType: "date" },
                endTime: { bsonType: ["date", "null"] },
                details: {
                    bsonType: "object",
                    additionalProperties: true,
                    properties: {
                        previousStatus: { bsonType: "string" },
                        newStatus: { bsonType: "string" },
                        confidence: { bsonType: "double", minimum: 0, maximum: 1 },
                        vehicleId: { bsonType: ["string", "null"] },
                        duration: { bsonType: ["int", "null"] }
                    }
                },
                severity: {
                    enum: ["info", "warning", "critical"]
                },
                acknowledged: { bsonType: "bool" },
                acknowledgedBy: { bsonType: ["string", "null"] },
                acknowledgedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 6. Violations collection
db.createCollection("violations", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["violationId", "type", "spotId", "timestamp", "status"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                violationId: {
                    bsonType: "string",
                    pattern: "^VIO[0-9]{10}$"
                },
                type: {
                    enum: [
                        "overstay",
                        "no_payment",
                        "invalid_permit",
                        "wrong_spot_type",
                        "outside_hours",
                        "double_parking",
                        "blocked_access"
                    ]
                },
                spotId: {
                    bsonType: "string",
                    pattern: "^SPOT[0-9]{8}$"
                },
                zoneId: {
                    bsonType: "string",
                    pattern: "^ZONE[0-9]{4}$"
                },
                vehicle: {
                    bsonType: "object",
                    properties: {
                        licensePlate: { bsonType: ["string", "null"] },
                        make: { bsonType: ["string", "null"] },
                        model: { bsonType: ["string", "null"] },
                        color: { bsonType: ["string", "null"] },
                        imageUrl: { bsonType: ["string", "null"] }
                    }
                },
                timestamp: { bsonType: "date" },
                detectedBy: {
                    enum: ["sensor", "camera", "officer", "user_report"]
                },
                fine: {
                    bsonType: "object",
                    required: ["amount", "currency"],
                    properties: {
                        amount: { bsonType: "double", minimum: 0 },
                        currency: { enum: ["USD", "EUR", "GBP"] },
                        dueDate: { bsonType: "date" }
                    }
                },
                status: {
                    enum: ["active", "paid", "disputed", "cancelled", "escalated"]
                },
                evidence: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            type: { enum: ["photo", "sensor_log", "video"] },
                            url: { bsonType: "string" },
                            timestamp: { bsonType: "date" }
                        }
                    }
                },
                officer: {
                    bsonType: ["object", "null"],
                    properties: {
                        badgeNumber: { bsonType: "string" },
                        name: { bsonType: "string" }
                    }
                },
                resolution: {
                    bsonType: ["object", "null"],
                    properties: {
                        status: { enum: ["paid", "dismissed", "reduced"] },
                        date: { bsonType: "date" },
                        amount: { bsonType: ["double", "null"] },
                        notes: { bsonType: "string" }
                    }
                }
            }
        }
    }
});

// =====================================================
// Create Indexes
// =====================================================

// Zones indexes
db.zones.createIndex({ zoneId: 1 }, { unique: true });
db.zones.createIndex({ "location.coordinates": "2dsphere" });
db.zones.createIndex({ type: 1 });

// Parking spots indexes
db.parking_spots.createIndex({ spotId: 1 }, { unique: true });
db.parking_spots.createIndex({ zoneId: 1, status: 1 });
db.parking_spots.createIndex({ "location.coordinates": "2dsphere" });
db.parking_spots.createIndex({ status: 1 });
db.parking_spots.createIndex({ type: 1, status: 1 });

// Sensors indexes
db.sensors.createIndex({ sensorId: 1 }, { unique: true });
db.sensors.createIndex({ spotId: 1 });
db.sensors.createIndex({ status: 1 });
db.sensors.createIndex({ "connectivity.lastSeen": -1 });

// Occupancy readings indexes (time-series optimized)
db.occupancy_readings.createIndex({ "meta.spotId": 1, timestamp: -1 });
db.occupancy_readings.createIndex({ "meta.sensorId": 1, timestamp: -1 });
db.occupancy_readings.createIndex({ "meta.zoneId": 1, timestamp: -1 });

// Events indexes
db.events.createIndex({ eventId: 1 }, { unique: true });
db.events.createIndex({ spotId: 1, timestamp: -1 });
db.events.createIndex({ eventType: 1, timestamp: -1 });
db.events.createIndex({ zoneId: 1, timestamp: -1 });
db.events.createIndex({ severity: 1, acknowledged: 1 });

// Violations indexes
db.violations.createIndex({ violationId: 1 }, { unique: true });
db.violations.createIndex({ spotId: 1, timestamp: -1 });
db.violations.createIndex({ status: 1 });
db.violations.createIndex({ type: 1, status: 1 });
db.violations.createIndex({ "vehicle.licensePlate": 1 });

print("\n" + "=".repeat(50));
print(`Database '${dbName}' setup complete!`);
print("Collections created: " + collections.join(", "));
print("Indexes and validation rules applied");
print("=" + "=".repeat(50) + "\n");