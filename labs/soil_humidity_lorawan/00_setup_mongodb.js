/**
 * MongoDB Setup Script for Soil Humidity LoRaWAN Monitoring
 *
 * Creates collections for agricultural soil monitoring using LoRaWAN sensors.
 * Demonstrates time-series data, IoT patterns, and agricultural analytics.
 *
 * Database: soil_humidity_lorawan
 * Usage: mongosh 00_setup_mongodb.js
 */

// Database configuration
const DATABASE_NAME = "soil_humidity_lorawan";

// Connect to MongoDB
conn = new Mongo();
db = conn.getDB(DATABASE_NAME);

print(`\n=== Setting up database: ${DATABASE_NAME} ===\n`);

// ============================================
// Helper Functions
// ============================================

function createCollectionIfNotExists(name, options = {}) {
    const collections = db.getCollectionNames();
    if (!collections.includes(name)) {
        db.createCollection(name, options);
        print(`[OK] Created collection: ${name}`);
    } else {
        print(`[OK] Collection exists: ${name}`);
    }
}

function createIndexSafely(collection, index, options = {}) {
    try {
        db[collection].createIndex(index, options);
        print(`[OK] Created index on ${collection}: ${JSON.stringify(index)}`);
    } catch (e) {
        if (e.codeName === 'IndexOptionsConflict' || e.code === 85) {
            print(`[OK] Index exists on ${collection}: ${JSON.stringify(index)}`);
        } else {
            throw e;
        }
    }
}

// ============================================
// Create Collections
// ============================================

print("\n--- Creating Collections ---");

// 1. Farms collection - Master data for agricultural sites
createCollectionIfNotExists("farms");

// 2. Fields collection - Individual field/plot information
createCollectionIfNotExists("fields");

// 3. Sensors collection - LoRaWAN soil sensors
createCollectionIfNotExists("sensors");

// 4. Measurements collection - Time-series soil data
createCollectionIfNotExists("measurements", {
    timeseries: {
        timeField: "ts",
        metaField: "meta",
        granularity: "minutes"  // Soil changes slowly, minute granularity is sufficient
    }
});

// 5. Irrigation schedules and events
createCollectionIfNotExists("irrigationEvents");

// 6. Alerts for soil conditions
createCollectionIfNotExists("alerts");

// 7. Crop types reference data
createCollectionIfNotExists("cropTypes");

// ============================================
// Create Indexes
// ============================================

print("\n--- Creating Indexes ---");

// Farms indexes
createIndexSafely("farms", { farmCode: 1 }, { unique: true });
createIndexSafely("farms", { createdAt: -1 });
createIndexSafely("farms", { "location": "2dsphere" });

// Fields indexes
createIndexSafely("fields", { fieldCode: 1 }, { unique: true });
createIndexSafely("fields", { farmId: 1, fieldCode: 1 });
createIndexSafely("fields", { farmId: 1, cropType: 1 });
createIndexSafely("fields", { "boundaries": "2dsphere" });

// Sensors indexes
createIndexSafely("sensors", { deviceEUI: 1 }, { unique: true });
createIndexSafely("sensors", { fieldId: 1, status: 1 });
createIndexSafely("sensors", { farmId: 1, sensorType: 1 });

// Irrigation events indexes
createIndexSafely("irrigationEvents", { fieldId: 1, scheduledAt: -1 });
createIndexSafely("irrigationEvents", { farmId: 1, status: 1 });

// Alerts indexes
createIndexSafely("alerts", { farmId: 1, timestamp: -1 });
createIndexSafely("alerts", { fieldId: 1, alertType: 1, status: 1 });
createIndexSafely("alerts", { severity: 1, status: 1 });

// Crop types indexes
createIndexSafely("cropTypes", { cropCode: 1 }, { unique: true });
createIndexSafely("cropTypes", { category: 1 });

// ============================================
// Schema Validation
// ============================================

print("\n--- Applying Schema Validators ---");

// Farms validation
db.runCommand({
    collMod: "farms",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["farmCode", "name", "ownerName", "location", "totalAreaHa", "createdAt", "updatedAt"],
            properties: {
                farmCode: {
                    bsonType: "string",
                    pattern: "^FARM_[0-9]{4}$",
                    description: "Unique farm identifier"
                },
                name: {
                    bsonType: "string",
                    minLength: 1,
                    maxLength: 100
                },
                ownerName: {
                    bsonType: "string"
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
                            items: { bsonType: "number" }
                        }
                    }
                },
                totalAreaHa: {
                    bsonType: "number",
                    minimum: 0,
                    description: "Total farm area in hectares"
                },
                isOrganic: {
                    bsonType: "bool"
                },
                createdAt: {
                    bsonType: "date"
                },
                updatedAt: {
                    bsonType: "date"
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to farms collection");

// Fields validation
db.runCommand({
    collMod: "fields",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["fieldCode", "farmId", "name", "areaHa", "cropType", "soilType", "createdAt", "updatedAt"],
            properties: {
                fieldCode: {
                    bsonType: "string",
                    pattern: "^FIELD_[A-Z0-9]+$"
                },
                farmId: {
                    bsonType: "objectId"
                },
                name: {
                    bsonType: "string"
                },
                areaHa: {
                    bsonType: "number",
                    minimum: 0
                },
                cropType: {
                    bsonType: "string"
                },
                soilType: {
                    enum: ["clay", "sandy", "loam", "silt", "peat", "chalk"],
                    description: "Soil composition type"
                },
                plantingDate: {
                    bsonType: "date"
                },
                harvestDate: {
                    bsonType: ["date", "null"]
                },
                boundaries: {
                    bsonType: "object",
                    description: "GeoJSON polygon for field boundaries"
                },
                irrigationSystem: {
                    enum: ["drip", "sprinkler", "flood", "pivot", "none"]
                },
                optimalMoisturePct: {
                    bsonType: "number",
                    minimum: 0,
                    maximum: 100,
                    description: "Optimal soil moisture percentage for current crop"
                },
                createdAt: {
                    bsonType: "date"
                },
                updatedAt: {
                    bsonType: "date"
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to fields collection");

// Sensors validation
db.runCommand({
    collMod: "sensors",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["deviceEUI", "farmId", "fieldId", "sensorType", "depthCm", "status", "installedAt"],
            properties: {
                deviceEUI: {
                    bsonType: "string",
                    pattern: "^[0-9A-F]{16}$",
                    description: "LoRaWAN Device EUI"
                },
                farmId: {
                    bsonType: "objectId"
                },
                fieldId: {
                    bsonType: "objectId"
                },
                sensorType: {
                    enum: ["soil_moisture", "soil_temperature", "soil_ph", "soil_ec", "multi_parameter"]
                },
                manufacturer: {
                    bsonType: "string"
                },
                model: {
                    bsonType: "string"
                },
                depthCm: {
                    bsonType: "number",
                    minimum: 0,
                    maximum: 200,
                    description: "Sensor depth in centimeters"
                },
                location: {
                    bsonType: "object",
                    description: "GeoJSON point for sensor location"
                },
                status: {
                    enum: ["ACTIVE", "INACTIVE", "MAINTENANCE", "FAILED"]
                },
                batteryPct: {
                    bsonType: "number",
                    minimum: 0,
                    maximum: 100
                },
                lastSeenAt: {
                    bsonType: "date"
                },
                installedAt: {
                    bsonType: "date"
                },
                calibratedAt: {
                    bsonType: ["date", "null"]
                },
                lorawanConfig: {
                    bsonType: "object",
                    properties: {
                        appEUI: { bsonType: "string" },
                        frequency: { bsonType: "number" },
                        spreadingFactor: { bsonType: "number" },
                        dataRate: { bsonType: "string" }
                    }
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to sensors collection");

// Irrigation events validation
db.runCommand({
    collMod: "irrigationEvents",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["farmId", "fieldId", "scheduledAt", "durationMinutes", "waterVolumeLiters", "status"],
            properties: {
                farmId: {
                    bsonType: "objectId"
                },
                fieldId: {
                    bsonType: "objectId"
                },
                scheduledAt: {
                    bsonType: "date"
                },
                startedAt: {
                    bsonType: ["date", "null"]
                },
                completedAt: {
                    bsonType: ["date", "null"]
                },
                durationMinutes: {
                    bsonType: "number",
                    minimum: 0
                },
                waterVolumeLiters: {
                    bsonType: "number",
                    minimum: 0
                },
                irrigationType: {
                    enum: ["scheduled", "manual", "automatic", "emergency"]
                },
                status: {
                    enum: ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED", "FAILED"]
                },
                triggeredBy: {
                    bsonType: "string",
                    description: "User ID or 'system' for automatic triggers"
                },
                notes: {
                    bsonType: ["string", "null"]
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to irrigationEvents collection");

// Alerts validation
db.runCommand({
    collMod: "alerts",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["farmId", "alertType", "severity", "status", "timestamp", "message"],
            properties: {
                farmId: {
                    bsonType: "objectId"
                },
                fieldId: {
                    bsonType: ["objectId", "null"]
                },
                sensorId: {
                    bsonType: ["objectId", "null"]
                },
                alertType: {
                    enum: [
                        "LOW_MOISTURE",
                        "HIGH_MOISTURE",
                        "SENSOR_OFFLINE",
                        "LOW_BATTERY",
                        "IRRIGATION_FAILURE",
                        "FROST_WARNING",
                        "HIGH_SALINITY"
                    ]
                },
                severity: {
                    enum: ["info", "warning", "critical"]
                },
                status: {
                    enum: ["OPEN", "ACKNOWLEDGED", "RESOLVED", "IGNORED"]
                },
                timestamp: {
                    bsonType: "date"
                },
                acknowledgedAt: {
                    bsonType: ["date", "null"]
                },
                resolvedAt: {
                    bsonType: ["date", "null"]
                },
                message: {
                    bsonType: "string"
                },
                metadata: {
                    bsonType: "object",
                    description: "Alert-specific data (thresholds, values, etc.)"
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to alerts collection");

// Crop types validation
db.runCommand({
    collMod: "cropTypes",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["cropCode", "name", "category", "optimalMoisturePct", "criticalMoisturePct", "growingDegreesDaysRequired"],
            properties: {
                cropCode: {
                    bsonType: "string",
                    pattern: "^CROP_[A-Z]+$"
                },
                name: {
                    bsonType: "string"
                },
                scientificName: {
                    bsonType: ["string", "null"]
                },
                category: {
                    enum: ["grain", "vegetable", "fruit", "legume", "root", "leafy", "other"]
                },
                optimalMoisturePct: {
                    bsonType: "object",
                    required: ["min", "max"],
                    properties: {
                        min: { bsonType: "number", minimum: 0, maximum: 100 },
                        max: { bsonType: "number", minimum: 0, maximum: 100 }
                    }
                },
                criticalMoisturePct: {
                    bsonType: "object",
                    required: ["min", "max"],
                    properties: {
                        min: { bsonType: "number", minimum: 0, maximum: 100 },
                        max: { bsonType: "number", minimum: 0, maximum: 100 }
                    }
                },
                optimalPhRange: {
                    bsonType: "object",
                    properties: {
                        min: { bsonType: "number", minimum: 0, maximum: 14 },
                        max: { bsonType: "number", minimum: 0, maximum: 14 }
                    }
                },
                growingDegreesDaysRequired: {
                    bsonType: "number",
                    minimum: 0,
                    description: "Total GDD required for maturity"
                },
                typicalGrowingDays: {
                    bsonType: "number",
                    minimum: 0
                },
                waterRequirementsLitersPerM2: {
                    bsonType: "number",
                    minimum: 0
                }
            }
        }
    },
    validationLevel: "moderate",
    validationAction: "error"
});
print("[OK] Applied validator to cropTypes collection");

// ============================================
// Summary
// ============================================

print("\n--- Setup Summary ---");
print(`Database: ${DATABASE_NAME}`);
print(`Collections: ${db.getCollectionNames().join(", ")}`);

// Show collection stats
db.getCollectionNames().forEach(collName => {
    const stats = db[collName].stats();
    const indexCount = db[collName].getIndexes().length;
    print(`  ${collName}: ${stats.count} documents, ${indexCount} indexes`);
});

print("\n[OK] Setup complete!");
print("\nNext steps:");
print("1. Run: python 01_seed_soil_humidity.py");
print("2. Run: python 02_simulate_soil_humidity.py");
print("3. Run: mongosh 03_queries_exam.js");