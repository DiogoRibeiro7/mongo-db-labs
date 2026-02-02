// =====================================================
// Cold Chain Monitoring - MongoDB Setup
// Database: coldchain_db
// Purpose: Temperature-controlled logistics monitoring
// =====================================================

// Use the database
const dbName = "coldchain_db";
const db = db.getSiblingDB(dbName);

print(`\nSetting up database: ${dbName}`);
print("=" + "=".repeat(50));

// Drop existing collections for clean setup
const collections = ["assets", "sensors", "measurements", "events", "routes", "alerts"];
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

// 1. Assets collection (fridges, freezers, trucks, containers)
db.createCollection("assets", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["assetId", "assetType", "name", "status", "location", "temperatureRange", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                assetId: {
                    bsonType: "string",
                    pattern: "^(FRG|FRZ|TRK|CTN)[0-9]{6}$",
                    description: "Asset ID with type prefix"
                },
                assetType: {
                    enum: ["refrigerator", "freezer", "truck", "container", "warehouse"],
                    description: "Type of cold chain asset"
                },
                name: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 100
                },
                status: {
                    enum: ["active", "inactive", "maintenance", "in_transit", "alarm"],
                    description: "Current asset status"
                },
                location: {
                    bsonType: "object",
                    required: ["type", "coordinates", "address"],
                    additionalProperties: false,
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
                        address: {
                            bsonType: "string",
                            maxLength: 200
                        }
                    }
                },
                temperatureRange: {
                    bsonType: "object",
                    required: ["min", "max", "optimal"],
                    additionalProperties: false,
                    properties: {
                        min: { bsonType: "double", minimum: -80, maximum: 30 },
                        max: { bsonType: "double", minimum: -80, maximum: 30 },
                        optimal: { bsonType: "double", minimum: -80, maximum: 30 },
                        unit: { enum: ["C", "F"] }
                    }
                },
                capacity: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        volume: { bsonType: "double", minimum: 0 },
                        unit: { enum: ["L", "m3", "ft3"] },
                        currentLoad: { bsonType: "double", minimum: 0, maximum: 100 }
                    }
                },
                owner: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        company: { bsonType: "string" },
                        contact: { bsonType: "string" },
                        phone: { bsonType: "string" }
                    }
                },
                compliance: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        certifications: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        },
                        lastInspection: { bsonType: "date" },
                        nextInspection: { bsonType: "date" }
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 2. Sensors collection
db.createCollection("sensors", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["sensorId", "assetId", "sensorType", "status", "installedAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                sensorId: {
                    bsonType: "string",
                    pattern: "^SEN[0-9]{8}$"
                },
                assetId: {
                    bsonType: "string",
                    pattern: "^(FRG|FRZ|TRK|CTN)[0-9]{6}$"
                },
                sensorType: {
                    enum: ["temperature", "humidity", "door", "gps", "shock", "power"],
                    description: "Type of sensor"
                },
                model: {
                    bsonType: "string",
                    maxLength: 50
                },
                status: {
                    enum: ["active", "inactive", "faulty", "calibrating"],
                    description: "Sensor status"
                },
                position: {
                    bsonType: "string",
                    description: "Physical position in asset (e.g., 'top_shelf', 'door', 'cargo_area')"
                },
                calibration: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        offset: { bsonType: "double", minimum: -10, maximum: 10 },
                        lastCalibrated: { bsonType: "date" },
                        nextCalibration: { bsonType: "date" }
                    }
                },
                batteryLevel: {
                    bsonType: "int",
                    minimum: 0,
                    maximum: 100
                },
                installedAt: { bsonType: "date" },
                lastReading: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 3. Measurements collection (time-series)
// Note: Time-series collections have built-in validation and don't support explicit validators
db.createCollection("measurements", {
    timeseries: {
        timeField: "timestamp",
        metaField: "meta",
        granularity: "seconds"
    }
});

// 4. Events collection (door opens, power failures, etc.)
db.createCollection("events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["eventId", "assetId", "eventType", "timestamp", "severity"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                eventId: {
                    bsonType: "string",
                    pattern: "^EVT[0-9]{10}$"
                },
                assetId: { bsonType: "string" },
                sensorId: { bsonType: ["string", "null"] },
                eventType: {
                    enum: [
                        "door_open", "door_close",
                        "power_failure", "power_restore",
                        "temperature_excursion", "humidity_excursion",
                        "shock_detected", "maintenance_start", "maintenance_end",
                        "route_start", "route_end", "geofence_entry", "geofence_exit"
                    ]
                },
                timestamp: { bsonType: "date" },
                endTime: { bsonType: ["date", "null"] },
                severity: {
                    enum: ["info", "warning", "critical"]
                },
                details: {
                    bsonType: "object",
                    additionalProperties: true
                },
                acknowledged: { bsonType: "bool" },
                acknowledgedBy: { bsonType: ["string", "null"] },
                acknowledgedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 5. Routes collection (transport routes)
db.createCollection("routes", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["routeId", "assetId", "origin", "destination", "status", "startTime"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                routeId: {
                    bsonType: "string",
                    pattern: "^RT[0-9]{8}$"
                },
                assetId: { bsonType: "string" },
                status: {
                    enum: ["planned", "in_progress", "completed", "cancelled", "delayed"]
                },
                origin: {
                    bsonType: "object",
                    required: ["name", "coordinates"],
                    properties: {
                        name: { bsonType: "string" },
                        coordinates: {
                            bsonType: "array",
                            minItems: 2,
                            maxItems: 2
                        }
                    }
                },
                destination: {
                    bsonType: "object",
                    required: ["name", "coordinates"],
                    properties: {
                        name: { bsonType: "string" },
                        coordinates: {
                            bsonType: "array",
                            minItems: 2,
                            maxItems: 2
                        }
                    }
                },
                waypoints: {
                    bsonType: ["array", "null"],
                    items: {
                        bsonType: "object",
                        properties: {
                            name: { bsonType: "string" },
                            coordinates: { bsonType: "array" },
                            arrivalTime: { bsonType: ["date", "null"] },
                            departureTime: { bsonType: ["date", "null"] }
                        }
                    }
                },
                cargo: {
                    bsonType: "object",
                    properties: {
                        description: { bsonType: "string" },
                        quantity: { bsonType: "int" },
                        value: { bsonType: "double" },
                        temperatureRequirement: {
                            bsonType: "object",
                            properties: {
                                min: { bsonType: "double" },
                                max: { bsonType: "double" }
                            }
                        }
                    }
                },
                startTime: { bsonType: "date" },
                expectedEndTime: { bsonType: "date" },
                actualEndTime: { bsonType: ["date", "null"] },
                distance: { bsonType: ["double", "null"] },
                duration: { bsonType: ["int", "null"] }
            }
        }
    }
});

// 6. Alerts collection
db.createCollection("alerts", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["alertId", "assetId", "alertType", "severity", "triggeredAt", "status"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                alertId: {
                    bsonType: "string",
                    pattern: "^ALT[0-9]{10}$"
                },
                assetId: { bsonType: "string" },
                sensorId: { bsonType: ["string", "null"] },
                routeId: { bsonType: ["string", "null"] },
                alertType: {
                    enum: [
                        "temperature_high", "temperature_low",
                        "humidity_high", "humidity_low",
                        "door_open_too_long", "power_failure",
                        "sensor_failure", "battery_low",
                        "route_delay", "geofence_violation"
                    ]
                },
                severity: {
                    enum: ["low", "medium", "high", "critical"]
                },
                status: {
                    enum: ["active", "acknowledged", "resolved", "escalated"]
                },
                threshold: {
                    bsonType: "object",
                    properties: {
                        metric: { bsonType: "string" },
                        operator: { enum: [">", "<", ">=", "<=", "==", "!="] },
                        value: { bsonType: "double" },
                        duration: { bsonType: "int" }
                    }
                },
                actualValue: { bsonType: ["double", "null"] },
                message: {
                    bsonType: "string",
                    maxLength: 500
                },
                triggeredAt: { bsonType: "date" },
                acknowledgedAt: { bsonType: ["date", "null"] },
                resolvedAt: { bsonType: ["date", "null"] },
                escalatedAt: { bsonType: ["date", "null"] },
                assignedTo: { bsonType: ["string", "null"] },
                notes: {
                    bsonType: ["array", "null"],
                    items: {
                        bsonType: "object",
                        properties: {
                            timestamp: { bsonType: "date" },
                            user: { bsonType: "string" },
                            note: { bsonType: "string" }
                        }
                    }
                }
            }
        }
    }
});

// =====================================================
// Create Indexes
// =====================================================

// Assets indexes
db.assets.createIndex({ assetId: 1 }, { unique: true });
db.assets.createIndex({ assetType: 1, status: 1 });
db.assets.createIndex({ "location.coordinates": "2dsphere" });

// Sensors indexes
db.sensors.createIndex({ sensorId: 1 }, { unique: true });
db.sensors.createIndex({ assetId: 1, sensorType: 1 });
db.sensors.createIndex({ status: 1 });

// Measurements indexes (time-series optimized)
db.measurements.createIndex({ "meta.assetId": 1, timestamp: -1 });
db.measurements.createIndex({ "meta.sensorId": 1, timestamp: -1 });
db.measurements.createIndex({ temperature: 1 });

// Events indexes
db.events.createIndex({ eventId: 1 }, { unique: true });
db.events.createIndex({ assetId: 1, timestamp: -1 });
db.events.createIndex({ eventType: 1, severity: 1 });
db.events.createIndex({ acknowledged: 1, severity: 1 });

// Routes indexes
db.routes.createIndex({ routeId: 1 }, { unique: true });
db.routes.createIndex({ assetId: 1, status: 1 });
db.routes.createIndex({ startTime: -1 });

// Alerts indexes
db.alerts.createIndex({ alertId: 1 }, { unique: true });
db.alerts.createIndex({ assetId: 1, status: 1, triggeredAt: -1 });
db.alerts.createIndex({ severity: 1, status: 1 });
db.alerts.createIndex({ alertType: 1, triggeredAt: -1 });

print("\n" + "=".repeat(50));
print(`Database '${dbName}' setup complete!`);
print("Collections created: " + collections.join(", "));
print("Indexes and validation rules applied");
print("=" + "=".repeat(50) + "\n");