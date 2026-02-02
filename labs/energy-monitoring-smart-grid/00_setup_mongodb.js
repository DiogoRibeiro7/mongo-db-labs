// =====================================================
// Smart Grid Energy Monitoring - MongoDB Setup
// Database: energygrid_db
// Purpose: Energy consumption monitoring and billing
// =====================================================

// Use the database
const dbName = "energygrid_db";
const db = db.getSiblingDB(dbName);

print(`\nSetting up database: ${dbName}`);
print("=" + "=".repeat(50));

// Drop existing collections for clean setup
const collections = ["buildings", "meters", "tariffs", "readings", "events", "bills"];
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

// 1. Buildings collection (residential, commercial, industrial)
db.createCollection("buildings", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["buildingId", "type", "name", "address", "status", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                buildingId: {
                    bsonType: "string",
                    pattern: "^BLD[0-9]{8}$",
                    description: "Building identifier"
                },
                type: {
                    enum: ["residential", "commercial", "industrial", "mixed"],
                    description: "Building type"
                },
                subType: {
                    enum: ["single_family", "apartment", "condo", "office", "retail", "warehouse",
                           "factory", "hospital", "school", "data_center", null],
                    description: "Specific building category"
                },
                name: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 100
                },
                address: {
                    bsonType: "object",
                    required: ["street", "city", "postalCode", "country"],
                    additionalProperties: false,
                    properties: {
                        street: { bsonType: "string" },
                        city: { bsonType: "string" },
                        state: { bsonType: "string" },
                        postalCode: { bsonType: "string" },
                        country: { bsonType: "string" },
                        coordinates: {
                            bsonType: "object",
                            properties: {
                                lat: { bsonType: "double", minimum: -90, maximum: 90 },
                                lng: { bsonType: "double", minimum: -180, maximum: 180 }
                            }
                        }
                    }
                },
                status: {
                    enum: ["active", "inactive", "construction", "renovation"],
                    description: "Building operational status"
                },
                characteristics: {
                    bsonType: "object",
                    additionalProperties: false,
                    properties: {
                        floors: { bsonType: "int", minimum: 1 },
                        units: { bsonType: "int", minimum: 1 },
                        squareMeters: { bsonType: "double", minimum: 0 },
                        yearBuilt: { bsonType: "int", minimum: 1800, maximum: 2100 },
                        energyClass: { enum: ["A", "B", "C", "D", "E", "F", "G", null] },
                        hasSolar: { bsonType: "bool" },
                        hasBackupPower: { bsonType: "bool" },
                        hasEVCharging: { bsonType: "bool" }
                    }
                },
                occupancy: {
                    bsonType: "object",
                    properties: {
                        residents: { bsonType: "int", minimum: 0 },
                        businesses: { bsonType: "int", minimum: 0 },
                        typicalOccupancy: {
                            bsonType: "object",
                            properties: {
                                weekday: { bsonType: "int", minimum: 0 },
                                weekend: { bsonType: "int", minimum: 0 }
                            }
                        }
                    }
                },
                contractInfo: {
                    bsonType: "object",
                    properties: {
                        accountNumber: { bsonType: "string" },
                        tariffPlanId: { bsonType: "string", pattern: "^TAR[0-9]{4}$" },
                        contractStart: { bsonType: "date" },
                        contractEnd: { bsonType: ["date", "null"] },
                        maxDemandKW: { bsonType: "double", minimum: 0 },
                        voltageLevel: { enum: ["LV", "MV", "HV"] }
                    }
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 2. Smart Meters collection
db.createCollection("meters", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["meterId", "buildingId", "type", "status", "installedAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                meterId: {
                    bsonType: "string",
                    pattern: "^MTR[0-9]{10}$",
                    description: "Smart meter serial number"
                },
                buildingId: {
                    bsonType: "string",
                    pattern: "^BLD[0-9]{8}$"
                },
                type: {
                    enum: ["electricity", "gas", "water", "solar", "battery"],
                    description: "Meter type"
                },
                subType: {
                    enum: ["single_phase", "three_phase", "net_metering", null],
                    description: "Specific meter configuration"
                },
                manufacturer: {
                    bsonType: "string",
                    maxLength: 50
                },
                model: {
                    bsonType: "string",
                    maxLength: 50
                },
                status: {
                    enum: ["active", "inactive", "faulty", "maintenance", "replaced"],
                    description: "Meter operational status"
                },
                capabilities: {
                    bsonType: "object",
                    properties: {
                        bidirectional: { bsonType: "bool" },
                        remoteDisconnect: { bsonType: "bool" },
                        powerQuality: { bsonType: "bool" },
                        tamperDetection: { bsonType: "bool" },
                        realtimeData: { bsonType: "bool" }
                    }
                },
                specifications: {
                    bsonType: "object",
                    properties: {
                        maxCurrent: { bsonType: "double", minimum: 0 },
                        maxVoltage: { bsonType: "double", minimum: 0 },
                        accuracy: { bsonType: "double", minimum: 0, maximum: 100 },
                        measurementInterval: { bsonType: "int", minimum: 1 }
                    }
                },
                connectivity: {
                    bsonType: "object",
                    properties: {
                        protocol: { enum: ["zigbee", "lorawan", "cellular", "plc", "wifi"] },
                        lastCommunication: { bsonType: "date" },
                        signalStrength: { bsonType: "int", minimum: -120, maximum: 0 },
                        firmwareVersion: { bsonType: "string" }
                    }
                },
                location: {
                    bsonType: "object",
                    properties: {
                        floor: { bsonType: ["int", "null"] },
                        unit: { bsonType: ["string", "null"] },
                        position: { bsonType: ["string", "null"] },
                        coordinates: {
                            bsonType: ["object", "null"],
                            properties: {
                                lat: { bsonType: "double" },
                                lng: { bsonType: "double" }
                            }
                        }
                    }
                },
                calibration: {
                    bsonType: "object",
                    properties: {
                        lastCalibrated: { bsonType: "date" },
                        nextCalibration: { bsonType: "date" },
                        calibrationFactor: { bsonType: "double" }
                    }
                },
                installedAt: { bsonType: "date" },
                replacedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 3. Tariffs collection
db.createCollection("tariffs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["tariffId", "name", "type", "validFrom", "rates"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                tariffId: {
                    bsonType: "string",
                    pattern: "^TAR[0-9]{4}$",
                    description: "Tariff plan identifier"
                },
                name: {
                    bsonType: "string",
                    minLength: 3,
                    maxLength: 100
                },
                type: {
                    enum: ["flat", "tiered", "time_of_use", "dynamic", "prepaid"],
                    description: "Tariff structure type"
                },
                customerType: {
                    enum: ["residential", "commercial", "industrial"],
                    description: "Target customer segment"
                },
                description: {
                    bsonType: "string",
                    maxLength: 500
                },
                validFrom: { bsonType: "date" },
                validUntil: { bsonType: ["date", "null"] },
                rates: {
                    bsonType: "object",
                    required: ["currency"],
                    properties: {
                        currency: { enum: ["USD", "EUR", "GBP"] },

                        // Flat rate
                        flatRate: {
                            bsonType: ["object", "null"],
                            properties: {
                                pricePerKWh: { bsonType: "double", minimum: 0 }
                            }
                        },

                        // Tiered rates
                        tiers: {
                            bsonType: ["array", "null"],
                            items: {
                                bsonType: "object",
                                properties: {
                                    minKWh: { bsonType: "double", minimum: 0 },
                                    maxKWh: { bsonType: ["double", "null"] },
                                    pricePerKWh: { bsonType: "double", minimum: 0 }
                                }
                            }
                        },

                        // Time of use rates
                        timeOfUse: {
                            bsonType: ["object", "null"],
                            properties: {
                                peak: {
                                    bsonType: "object",
                                    properties: {
                                        hours: {
                                            bsonType: "array",
                                            items: {
                                                bsonType: "object",
                                                properties: {
                                                    start: { bsonType: "string", pattern: "^[0-2][0-9]:[0-5][0-9]$" },
                                                    end: { bsonType: "string", pattern: "^[0-2][0-9]:[0-5][0-9]$" }
                                                }
                                            }
                                        },
                                        pricePerKWh: { bsonType: "double", minimum: 0 }
                                    }
                                },
                                offPeak: {
                                    bsonType: "object",
                                    properties: {
                                        pricePerKWh: { bsonType: "double", minimum: 0 }
                                    }
                                },
                                shoulder: {
                                    bsonType: ["object", "null"],
                                    properties: {
                                        hours: { bsonType: "array" },
                                        pricePerKWh: { bsonType: "double", minimum: 0 }
                                    }
                                }
                            }
                        },

                        // Fixed charges
                        fixedCharges: {
                            bsonType: "object",
                            properties: {
                                monthlyCharge: { bsonType: "double", minimum: 0 },
                                connectionCharge: { bsonType: "double", minimum: 0 },
                                demandCharge: { bsonType: ["double", "null"], minimum: 0 }
                            }
                        },

                        // Taxes and fees
                        taxes: {
                            bsonType: "array",
                            items: {
                                bsonType: "object",
                                properties: {
                                    name: { bsonType: "string" },
                                    rate: { bsonType: "double", minimum: 0, maximum: 1 },
                                    fixedAmount: { bsonType: ["double", "null"] }
                                }
                            }
                        }
                    }
                },
                incentives: {
                    bsonType: ["object", "null"],
                    properties: {
                        solarFeedIn: { bsonType: "double", minimum: 0 },
                        evCharging: { bsonType: "double", minimum: 0 },
                        greenEnergy: { bsonType: "double", minimum: 0 }
                    }
                },
                penalties: {
                    bsonType: ["object", "null"],
                    properties: {
                        exceededDemand: { bsonType: "double", minimum: 0 },
                        powerFactor: { bsonType: "double", minimum: 0 },
                        latePayment: { bsonType: "double", minimum: 0 }
                    }
                }
            }
        }
    }
});

// 4. Readings collection (time-series)
// Note: Time-series collections don't support validators
db.createCollection("readings", {
    timeseries: {
        timeField: "timestamp",
        metaField: "meta",
        granularity: "minutes"
    }
});

// 5. Events collection
db.createCollection("events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["eventId", "eventType", "timestamp", "severity"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                eventId: {
                    bsonType: "string",
                    pattern: "^EVT[0-9]{12}$"
                },
                eventType: {
                    enum: [
                        "power_outage",
                        "power_restored",
                        "peak_demand",
                        "voltage_sag",
                        "voltage_spike",
                        "frequency_deviation",
                        "meter_tamper",
                        "meter_failure",
                        "overconsumption",
                        "underconsumption",
                        "phase_imbalance",
                        "power_quality_issue"
                    ]
                },
                meterId: {
                    bsonType: ["string", "null"],
                    pattern: "^MTR[0-9]{10}$"
                },
                buildingId: {
                    bsonType: ["string", "null"],
                    pattern: "^BLD[0-9]{8}$"
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
                        duration: { bsonType: ["int", "null"] },
                        affectedUnits: { bsonType: ["int", "null"] },
                        peakValue: { bsonType: ["double", "null"] },
                        thresholdExceeded: { bsonType: ["double", "null"] },
                        estimatedCost: { bsonType: ["double", "null"] }
                    }
                },
                location: {
                    bsonType: ["object", "null"],
                    properties: {
                        grid: { bsonType: "string" },
                        substation: { bsonType: "string" },
                        feeder: { bsonType: "string" }
                    }
                },
                response: {
                    bsonType: ["object", "null"],
                    properties: {
                        automated: { bsonType: "bool" },
                        action: { bsonType: "string" },
                        timestamp: { bsonType: "date" },
                        result: { bsonType: "string" }
                    }
                },
                acknowledged: { bsonType: "bool" },
                acknowledgedBy: { bsonType: ["string", "null"] },
                acknowledgedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// 6. Bills collection
db.createCollection("bills", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["billId", "buildingId", "billingPeriod", "status", "totalAmount", "createdAt"],
            additionalProperties: false,
            properties: {
                _id: { bsonType: "objectId" },
                billId: {
                    bsonType: "string",
                    pattern: "^BILL[0-9]{10}$"
                },
                buildingId: {
                    bsonType: "string",
                    pattern: "^BLD[0-9]{8}$"
                },
                accountNumber: { bsonType: "string" },
                billingPeriod: {
                    bsonType: "object",
                    required: ["start", "end"],
                    properties: {
                        start: { bsonType: "date" },
                        end: { bsonType: "date" },
                        days: { bsonType: "int", minimum: 1 }
                    }
                },
                consumption: {
                    bsonType: "object",
                    required: ["totalKWh"],
                    properties: {
                        totalKWh: { bsonType: "double", minimum: 0 },
                        peakKWh: { bsonType: "double", minimum: 0 },
                        offPeakKWh: { bsonType: "double", minimum: 0 },
                        shoulderKWh: { bsonType: ["double", "null"], minimum: 0 },
                        peakDemandKW: { bsonType: "double", minimum: 0 },
                        averageDailyKWh: { bsonType: "double", minimum: 0 },
                        powerFactor: { bsonType: "double", minimum: 0, maximum: 1 }
                    }
                },
                charges: {
                    bsonType: "object",
                    required: ["energyCharge", "total"],
                    properties: {
                        energyCharge: { bsonType: "double", minimum: 0 },
                        demandCharge: { bsonType: ["double", "null"], minimum: 0 },
                        fixedCharge: { bsonType: ["double", "null"], minimum: 0 },
                        taxes: { bsonType: "double", minimum: 0 },
                        adjustments: { bsonType: ["double", "null"] },
                        credits: { bsonType: ["double", "null"] },
                        total: { bsonType: "double" }
                    }
                },
                tariffApplied: {
                    bsonType: "object",
                    properties: {
                        tariffId: { bsonType: "string", pattern: "^TAR[0-9]{4}$" },
                        name: { bsonType: "string" },
                        rates: {
                            bsonType: "object",
                            properties: {
                                peak: { bsonType: ["double", "null"] },
                                offPeak: { bsonType: ["double", "null"] },
                                flat: { bsonType: ["double", "null"] }
                            }
                        }
                    }
                },
                comparison: {
                    bsonType: ["object", "null"],
                    properties: {
                        previousMonth: { bsonType: "double" },
                        previousYear: { bsonType: "double" },
                        percentChange: { bsonType: "double" }
                    }
                },
                status: {
                    enum: ["draft", "issued", "sent", "paid", "overdue", "disputed"],
                    description: "Bill status"
                },
                totalAmount: { bsonType: "double" },
                currency: { enum: ["USD", "EUR", "GBP"] },
                dueDate: { bsonType: "date" },
                issuedAt: { bsonType: "date" },
                paidAt: { bsonType: ["date", "null"] },
                paymentMethod: {
                    enum: ["credit_card", "bank_transfer", "direct_debit", "cash", "check", null]
                },
                createdAt: { bsonType: "date" },
                updatedAt: { bsonType: ["date", "null"] }
            }
        }
    }
});

// =====================================================
// Create Indexes
// =====================================================

// Buildings indexes
db.buildings.createIndex({ buildingId: 1 }, { unique: true });
db.buildings.createIndex({ type: 1, status: 1 });
db.buildings.createIndex({ "address.postalCode": 1 });
db.buildings.createIndex({ "contractInfo.tariffPlanId": 1 });

// Meters indexes
db.meters.createIndex({ meterId: 1 }, { unique: true });
db.meters.createIndex({ buildingId: 1, type: 1 });
db.meters.createIndex({ status: 1 });
db.meters.createIndex({ "connectivity.lastCommunication": -1 });

// Tariffs indexes
db.tariffs.createIndex({ tariffId: 1 }, { unique: true });
db.tariffs.createIndex({ type: 1, customerType: 1 });
db.tariffs.createIndex({ validFrom: 1, validUntil: 1 });

// Readings indexes (time-series optimized)
db.readings.createIndex({ "meta.meterId": 1, timestamp: -1 });
db.readings.createIndex({ "meta.buildingId": 1, timestamp: -1 });
db.readings.createIndex({ timestamp: -1 });

// Events indexes
db.events.createIndex({ eventId: 1 }, { unique: true });
db.events.createIndex({ buildingId: 1, timestamp: -1 });
db.events.createIndex({ meterId: 1, timestamp: -1 });
db.events.createIndex({ eventType: 1, severity: 1 });
db.events.createIndex({ timestamp: -1, severity: 1 });

// Bills indexes
db.bills.createIndex({ billId: 1 }, { unique: true });
db.bills.createIndex({ buildingId: 1, "billingPeriod.start": -1 });
db.bills.createIndex({ status: 1, dueDate: 1 });
db.bills.createIndex({ accountNumber: 1 });

print("\n" + "=".repeat(50));
print(`Database '${dbName}' setup complete!`);
print("Collections created: " + collections.join(", "));
print("Indexes and validation rules applied");
print("=" + "=".repeat(50) + "\n");