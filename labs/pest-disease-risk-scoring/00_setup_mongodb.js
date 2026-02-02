// =====================================================
// Agricultural Pest & Disease Risk Scoring - MongoDB Setup
// Database: agrimonitor_db
// Purpose: Multi-farm pest and disease risk monitoring
// =====================================================

// Use the database
const dbName = "agrimonitor_db";
const db = db.getSiblingDB(dbName);

print(`\nSetting up database: ${dbName}`);
print("=" + "=".repeat(50));

// Drop existing collections for clean setup
const collections = ["farms", "fields", "sensors", "measurements", "risk_assessments", "events"];
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

// 1. Farms collection
db.createCollection("farms", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["farmId", "name", "location", "size", "status", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                farmId: {
                    bsonType: "string",
                    pattern: "^FRM[0-9]{6}$",
                    description: "Farm identifier"
                },
                name: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 100
                },
                owner: {
                    bsonType: "object",
                    properties: {
                        name: { bsonType: "string" },
                        contact: { bsonType: "string" },
                        email: {
                            bsonType: "string",
                            pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                        }
                    }
                },
                location: {
                    bsonType: "object",
                    required: ["coordinates", "region", "country"],
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
                        region: { bsonType: "string" },
                        country: { bsonType: "string" },
                        elevation: { bsonType: "double", minimum: -500, maximum: 9000 }
                    }
                },
                size: {
                    bsonType: "object",
                    required: ["total", "unit"],
                    properties: {
                        total: { bsonType: "double", minimum: 0 },
                        cultivated: { bsonType: "double", minimum: 0 },
                        unit: { enum: ["hectares", "acres"] }
                    }
                },
                certification: {
                    bsonType: "object",
                    properties: {
                        organic: { bsonType: "bool" },
                        globalGAP: { bsonType: "bool" },
                        fairTrade: { bsonType: "bool" },
                        certifications: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        }
                    }
                },
                management: {
                    bsonType: "object",
                    properties: {
                        ipmEnabled: { bsonType: "bool" },
                        sprayProtocol: { enum: ["preventive", "curative", "integrated", "organic"] },
                        monitoringFrequency: { enum: ["daily", "twice_weekly", "weekly", "biweekly"] }
                    }
                },
                status: {
                    enum: ["active", "inactive", "seasonal", "quarantine"],
                    description: "Farm operational status"
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 2. Fields collection (individual plots within farms)
db.createCollection("fields", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["fieldId", "farmId", "name", "crop", "area", "plantingDate", "status"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                fieldId: {
                    bsonType: "string",
                    pattern: "^FLD[0-9]{8}$",
                    description: "Field identifier"
                },
                farmId: {
                    bsonType: "string",
                    pattern: "^FRM[0-9]{6}$"
                },
                name: {
                    bsonType: "string",
                    description: "Field name or plot number"
                },
                crop: {
                    bsonType: "object",
                    required: ["type", "variety"],
                    properties: {
                        type: {
                            enum: ["wheat", "corn", "soybean", "rice", "cotton", "potato",
                                   "tomato", "grape", "apple", "citrus", "vegetables", "other"]
                        },
                        variety: { bsonType: "string" },
                        growthStage: {
                            enum: ["seedling", "vegetative", "flowering", "fruiting", "maturity", "harvest"]
                        }
                    }
                },
                area: {
                    bsonType: "object",
                    required: ["size", "unit"],
                    properties: {
                        size: { bsonType: "double", minimum: 0 },
                        unit: { enum: ["hectares", "acres"] },
                        geometry: {
                            bsonType: "object",
                            properties: {
                                type: { enum: ["Polygon"] },
                                coordinates: { bsonType: "array" }
                            }
                        }
                    }
                },
                soil: {
                    bsonType: "object",
                    properties: {
                        type: { enum: ["clay", "sandy", "loam", "silt", "peat", "chalky"] },
                        pH: { bsonType: "double", minimum: 3.0, maximum: 10.0 },
                        organic_matter: { bsonType: "double", minimum: 0, maximum: 100 },
                        drainage: { enum: ["excellent", "good", "moderate", "poor"] }
                    }
                },
                irrigation: {
                    bsonType: "object",
                    properties: {
                        type: { enum: ["drip", "sprinkler", "flood", "rainfed", "pivot"] },
                        automated: { bsonType: "bool" },
                        schedule: { bsonType: "string" }
                    }
                },
                plantingDate: { bsonType: "date" },
                expectedHarvest: { bsonType: ["date", "null"] },
                lastSpray: {
                    bsonType: ["object", "null"],
                    properties: {
                        date: { bsonType: "date" },
                        product: { bsonType: "string" },
                        reason: { bsonType: "string" },
                        effectiveness: { enum: ["excellent", "good", "moderate", "poor", null] }
                    }
                },
                status: {
                    enum: ["planted", "growing", "harvesting", "fallow", "preparing"],
                    description: "Field status"
                },
                riskHistory: {
                    bsonType: "object",
                    properties: {
                        lastHighRisk: { bsonType: ["date", "null"] },
                        totalSprayEvents: { bsonType: "int", minimum: 0 },
                        commonPests: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        },
                        commonDiseases: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        }
                    }
                }
            }
        }
    }
});

// 3. Sensors collection
db.createCollection("sensors", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["sensorId", "type", "fieldId", "status", "installedAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                sensorId: {
                    bsonType: "string",
                    pattern: "^SEN[0-9]{10}$"
                },
                type: {
                    enum: ["leaf_wetness", "air_temperature", "relative_humidity",
                           "rainfall", "trap_count", "soil_moisture", "wind_speed",
                           "solar_radiation", "soil_temperature"],
                    description: "Sensor type"
                },
                subType: {
                    bsonType: ["string", "null"],
                    description: "Specific model or pest type for traps"
                },
                fieldId: {
                    bsonType: "string",
                    pattern: "^FLD[0-9]{8}$"
                },
                farmId: {
                    bsonType: ["string", "null"],
                    pattern: "^FRM[0-9]{6}$"
                },
                location: {
                    bsonType: "object",
                    properties: {
                        coordinates: {
                            bsonType: "array",
                            minItems: 2,
                            maxItems: 2
                        },
                        height: { bsonType: "double", description: "Height above ground in meters" },
                        position: { bsonType: "string", description: "Description of placement" }
                    }
                },
                manufacturer: { bsonType: ["string", "null"] },
                model: { bsonType: ["string", "null"] },
                status: {
                    enum: ["active", "inactive", "maintenance", "faulty", "calibrating"],
                    description: "Sensor status"
                },
                specifications: {
                    bsonType: "object",
                    properties: {
                        accuracy: { bsonType: "double", minimum: 0, maximum: 100 },
                        range: {
                            bsonType: "object",
                            properties: {
                                min: { bsonType: "double" },
                                max: { bsonType: "double" }
                            }
                        },
                        measurementInterval: { bsonType: "int", minimum: 1 }
                    }
                },
                connectivity: {
                    bsonType: "object",
                    properties: {
                        protocol: { enum: ["LoRa", "Sigfox", "NB-IoT", "WiFi", "cellular"] },
                        batteryLevel: { bsonType: "int", minimum: 0, maximum: 100 },
                        lastCommunication: { bsonType: "date" },
                        signalStrength: { bsonType: "int" }
                    }
                },
                calibration: {
                    bsonType: "object",
                    properties: {
                        lastCalibrated: { bsonType: "date" },
                        nextCalibration: { bsonType: "date" },
                        offset: { bsonType: "double" }
                    }
                },
                trapDetails: {
                    bsonType: ["object", "null"],
                    properties: {
                        targetPest: { bsonType: "string" },
                        lureType: { bsonType: "string" },
                        lureExpiry: { bsonType: "date" },
                        trapCapacity: { bsonType: "int" }
                    }
                },
                installedAt: { bsonType: "date" },
                replacedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 4. Measurements collection (time-series)
// Note: Time-series collections don't support validators
db.createCollection("measurements", {
    timeseries: {
        timeField: "timestamp",
        metaField: "meta",
        granularity: "minutes"
    }
});

// 5. Risk Assessments collection
db.createCollection("risk_assessments", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["assessmentId", "fieldId", "timestamp", "riskScore", "factors", "recommendation"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                assessmentId: {
                    bsonType: "string",
                    pattern: "^RSK[0-9]{12}$"
                },
                fieldId: {
                    bsonType: "string",
                    pattern: "^FLD[0-9]{8}$"
                },
                farmId: {
                    bsonType: "string",
                    pattern: "^FRM[0-9]{6}$"
                },
                timestamp: { bsonType: "date" },
                riskScore: {
                    bsonType: "double",
                    minimum: 0,
                    maximum: 100,
                    description: "Overall risk score 0-100"
                },
                riskLevel: {
                    enum: ["low", "moderate", "high", "critical"],
                    description: "Risk category"
                },
                factors: {
                    bsonType: "object",
                    required: ["leafWetness", "temperature", "humidity"],
                    properties: {
                        leafWetness: {
                            bsonType: "object",
                            properties: {
                                value: { bsonType: "double" },
                                weight: { bsonType: "double" },
                                contribution: { bsonType: "double" }
                            }
                        },
                        temperature: {
                            bsonType: "object",
                            properties: {
                                value: { bsonType: "double" },
                                weight: { bsonType: "double" },
                                contribution: { bsonType: "double" },
                                optimal: { bsonType: "bool" }
                            }
                        },
                        humidity: {
                            bsonType: "object",
                            properties: {
                                value: { bsonType: "double" },
                                weight: { bsonType: "double" },
                                contribution: { bsonType: "double" }
                            }
                        },
                        rainfall: {
                            bsonType: "object",
                            properties: {
                                value: { bsonType: "double" },
                                weight: { bsonType: "double" },
                                contribution: { bsonType: "double" },
                                recent24h: { bsonType: "double" },
                                recent72h: { bsonType: "double" }
                            }
                        },
                        trapCount: {
                            bsonType: "object",
                            properties: {
                                value: { bsonType: "int" },
                                weight: { bsonType: "double" },
                                contribution: { bsonType: "double" },
                                trend: { enum: ["increasing", "stable", "decreasing"] },
                                threshold: { bsonType: "int" }
                            }
                        }
                    }
                },
                diseases: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            name: { bsonType: "string" },
                            probability: { bsonType: "double", minimum: 0, maximum: 100 },
                            conditions_met: { bsonType: "int" },
                            total_conditions: { bsonType: "int" }
                        }
                    }
                },
                pests: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            name: { bsonType: "string" },
                            population: { enum: ["low", "moderate", "high", "outbreak"] },
                            trapCount: { bsonType: "int" },
                            economicThreshold: { bsonType: "int" }
                        }
                    }
                },
                recommendation: {
                    bsonType: "object",
                    required: ["action", "priority"],
                    properties: {
                        action: {
                            enum: ["no_action", "monitor_closely", "preventive_spray",
                                   "curative_spray", "immediate_action"],
                            description: "Recommended action"
                        },
                        priority: {
                            enum: ["low", "medium", "high", "urgent"],
                            description: "Action priority"
                        },
                        products: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    name: { bsonType: "string" },
                                    type: { enum: ["fungicide", "insecticide", "herbicide", "biological"] },
                                    dosage: { bsonType: "string" },
                                    rei: { bsonType: "int", description: "Re-entry interval in hours" },
                                    phi: { bsonType: "int", description: "Pre-harvest interval in days" }
                                }
                            }
                        },
                        timing: { bsonType: "string" },
                        notes: { bsonType: "string" }
                    }
                },
                explanation: {
                    bsonType: "string",
                    description: "Human-readable explanation of risk calculation"
                },
                confidence: {
                    bsonType: "double",
                    minimum: 0,
                    maximum: 100,
                    description: "Confidence level in assessment"
                }
            }
        }
    }
});

// 6. Events collection
db.createCollection("events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["eventId", "eventType", "fieldId", "timestamp", "severity"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                eventId: {
                    bsonType: "string",
                    pattern: "^EVT[0-9]{12}$"
                },
                eventType: {
                    enum: [
                        "SPRAY_RECOMMENDATION",
                        "RISK_ALERT",
                        "PEST_OUTBREAK",
                        "DISEASE_DETECTION",
                        "WEATHER_WARNING",
                        "TRAP_THRESHOLD",
                        "SPRAY_COMPLETED",
                        "SENSOR_ALERT"
                    ]
                },
                fieldId: {
                    bsonType: "string",
                    pattern: "^FLD[0-9]{8}$"
                },
                farmId: {
                    bsonType: "string",
                    pattern: "^FRM[0-9]{6}$"
                },
                timestamp: { bsonType: "date" },
                endTime: { bsonType: ["date", "null"] },
                severity: {
                    enum: ["info", "warning", "critical", "emergency"]
                },
                details: {
                    bsonType: "object",
                    additionalProperties: true,
                    properties: {
                        riskScore: { bsonType: ["double", "null"] },
                        affectedArea: { bsonType: ["double", "null"] },
                        pestName: { bsonType: ["string", "null"] },
                        diseaseName: { bsonType: ["string", "null"] },
                        trapCount: { bsonType: ["int", "null"] },
                        conditions: { bsonType: ["object", "null"] },
                        recommendedAction: { bsonType: ["string", "null"] },
                        economicImpact: { bsonType: ["double", "null"] }
                    }
                },
                response: {
                    bsonType: ["object", "null"],
                    properties: {
                        action: { bsonType: "string" },
                        timestamp: { bsonType: "date" },
                        implementedBy: { bsonType: "string" },
                        result: { bsonType: "string" },
                        notes: { bsonType: "string" }
                    }
                },
                acknowledged: { bsonType: "bool" },
                acknowledgedBy: { bsonType: ["string", "null"] },
                acknowledgedAt: { bsonType: ["date", "null"] },
                notifications: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            method: { enum: ["sms", "email", "app", "webhook"] },
                            recipient: { bsonType: "string" },
                            sentAt: { bsonType: "date" },
                            status: { enum: ["sent", "delivered", "failed"] }
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

// Farms indexes
db.farms.createIndex({ farmId: 1 }, { unique: true });
db.farms.createIndex({ "location.coordinates": "2dsphere" });
db.farms.createIndex({ status: 1 });

// Fields indexes
db.fields.createIndex({ fieldId: 1 }, { unique: true });
db.fields.createIndex({ farmId: 1, status: 1 });
db.fields.createIndex({ "crop.type": 1, "crop.growthStage": 1 });
db.fields.createIndex({ "area.geometry": "2dsphere" }, { sparse: true });

// Sensors indexes
db.sensors.createIndex({ sensorId: 1 }, { unique: true });
db.sensors.createIndex({ fieldId: 1, type: 1 });
db.sensors.createIndex({ farmId: 1, status: 1 });
db.sensors.createIndex({ type: 1, status: 1 });

// Measurements indexes (time-series optimized)
db.measurements.createIndex({ "meta.fieldId": 1, timestamp: -1 });
db.measurements.createIndex({ "meta.sensorId": 1, timestamp: -1 });
db.measurements.createIndex({ "meta.farmId": 1, timestamp: -1 });
db.measurements.createIndex({ "meta.sensorType": 1, timestamp: -1 });

// Risk Assessments indexes
db.risk_assessments.createIndex({ assessmentId: 1 }, { unique: true });
db.risk_assessments.createIndex({ fieldId: 1, timestamp: -1 });
db.risk_assessments.createIndex({ farmId: 1, timestamp: -1 });
db.risk_assessments.createIndex({ riskScore: -1 });
db.risk_assessments.createIndex({ riskLevel: 1, timestamp: -1 });

// Events indexes
db.events.createIndex({ eventId: 1 }, { unique: true });
db.events.createIndex({ fieldId: 1, timestamp: -1 });
db.events.createIndex({ farmId: 1, timestamp: -1 });
db.events.createIndex({ eventType: 1, severity: 1 });
db.events.createIndex({ timestamp: -1, severity: 1 });

print("\n" + "=".repeat(50));
print(`Database '${dbName}' setup complete!`);
print("Collections created: " + collections.join(", "));
print("Indexes and validation rules applied");
print("=" + "=".repeat(50) + "\n");