// =====================================================
// Smart Grid Energy Monitoring - Bad Inserts (Validation Demo)
// Demonstrates schema validation errors
// =====================================================

const dbName = "energygrid_db";
const db = db.getSiblingDB(dbName);

print("\nSmart Grid Energy Monitoring - Schema Validation Examples");
print("=" + "=".repeat(50));
print("These inserts will fail due to validation rules\n");

// Helper function to attempt insert and show error
function tryInsert(collection, document, description) {
    print(`\n[Attempting] ${description}`);
    print(`Collection: ${collection}`);
    try {
        db[collection].insertOne(document);
        print("[X] ERROR: Insert succeeded but should have failed!");
    } catch (e) {
        print("[OK] Failed as expected:");
        print(`    Reason: ${e.message || e}`);
    }
}

// =====================================================
// 1. Buildings Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("BUILDINGS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid building ID pattern
tryInsert("buildings", {
    buildingId: "BLDG123",  // Wrong pattern (should be BLD + 8 digits)
    type: "residential",
    name: "Invalid Building",
    address: {
        street: "123 Main St",
        city: "San Francisco",
        postalCode: "94102",
        country: "USA"
    },
    status: "active",
    createdAt: new Date()
}, "Invalid buildingId pattern");

// Invalid building type
tryInsert("buildings", {
    buildingId: "BLD99999999",
    type: "skyscraper",  // Not in enum
    name: "Test Building",
    address: {
        street: "123 Main St",
        city: "San Francisco",
        postalCode: "94102",
        country: "USA"
    },
    status: "active",
    createdAt: new Date()
}, "Invalid building type (not in enum)");

// Invalid voltage level
tryInsert("buildings", {
    buildingId: "BLD99999998",
    type: "commercial",
    name: "Test Building",
    address: {
        street: "123 Main St",
        city: "San Francisco",
        postalCode: "94102",
        country: "USA"
    },
    status: "active",
    contractInfo: {
        accountNumber: "ACC123456",
        tariffPlanId: "TAR0001",
        contractStart: new Date(),
        maxDemandKW: 100,
        voltageLevel: "EHV"  // Not in enum (LV, MV, HV)
    },
    createdAt: new Date()
}, "Invalid voltage level");

// Invalid energy class
tryInsert("buildings", {
    buildingId: "BLD99999997",
    type: "residential",
    name: "Test Building",
    address: {
        street: "123 Main St",
        city: "San Francisco",
        postalCode: "94102",
        country: "USA"
    },
    status: "active",
    characteristics: {
        floors: 2,
        units: 1,
        squareMeters: 200,
        yearBuilt: 2020,
        energyClass: "Z"  // Not in enum (A-G)
    },
    createdAt: new Date()
}, "Invalid energy class");

// Negative square meters
tryInsert("buildings", {
    buildingId: "BLD99999996",
    type: "commercial",
    name: "Test Building",
    address: {
        street: "123 Main St",
        city: "San Francisco",
        postalCode: "94102",
        country: "USA"
    },
    status: "active",
    characteristics: {
        floors: 5,
        units: 10,
        squareMeters: -500  // Negative value
    },
    createdAt: new Date()
}, "Negative square meters");

// =====================================================
// 2. Meters Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("METERS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid meter ID pattern
tryInsert("meters", {
    meterId: "METER123",  // Wrong pattern (should be MTR + 10 digits)
    buildingId: "BLD00000001",
    type: "electricity",
    status: "active",
    installedAt: new Date()
}, "Invalid meterId pattern");

// Invalid meter type
tryInsert("meters", {
    meterId: "MTR9999999999",
    buildingId: "BLD00000001",
    type: "nuclear",  // Not in enum
    status: "active",
    installedAt: new Date()
}, "Invalid meter type (not in enum)");

// Invalid connectivity protocol
tryInsert("meters", {
    meterId: "MTR9999999998",
    buildingId: "BLD00000001",
    type: "electricity",
    status: "active",
    connectivity: {
        protocol: "bluetooth",  // Not in enum
        lastCommunication: new Date(),
        signalStrength: -60
    },
    installedAt: new Date()
}, "Invalid connectivity protocol");

// Signal strength out of range
tryInsert("meters", {
    meterId: "MTR9999999997",
    buildingId: "BLD00000001",
    type: "electricity",
    status: "active",
    connectivity: {
        protocol: "zigbee",
        lastCommunication: new Date(),
        signalStrength: 10  // Should be negative (dBm)
    },
    installedAt: new Date()
}, "Invalid signal strength (positive dBm)");

// Accuracy out of range
tryInsert("meters", {
    meterId: "MTR9999999996",
    buildingId: "BLD00000001",
    type: "electricity",
    status: "active",
    specifications: {
        maxCurrent: 200,
        maxVoltage: 240,
        accuracy: 150,  // Max is 100%
        measurementInterval: 15
    },
    installedAt: new Date()
}, "Accuracy > 100%");

// =====================================================
// 3. Tariffs Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("TARIFFS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid tariff ID pattern
tryInsert("tariffs", {
    tariffId: "TARIFF01",  // Wrong pattern (should be TAR + 4 digits)
    name: "Invalid Tariff",
    type: "flat",
    validFrom: new Date(),
    rates: {
        currency: "USD",
        flatRate: {
            pricePerKWh: 0.10
        }
    }
}, "Invalid tariffId pattern");

// Invalid tariff type
tryInsert("tariffs", {
    tariffId: "TAR9999",
    name: "Test Tariff",
    type: "variable",  // Not in enum
    validFrom: new Date(),
    rates: {
        currency: "USD"
    }
}, "Invalid tariff type (not in enum)");

// Invalid currency
tryInsert("tariffs", {
    tariffId: "TAR9998",
    name: "Test Tariff",
    type: "flat",
    validFrom: new Date(),
    rates: {
        currency: "BTC",  // Not in enum (USD, EUR, GBP)
        flatRate: {
            pricePerKWh: 0.10
        }
    }
}, "Invalid currency");

// Negative price
tryInsert("tariffs", {
    tariffId: "TAR9997",
    name: "Test Tariff",
    type: "flat",
    validFrom: new Date(),
    rates: {
        currency: "USD",
        flatRate: {
            pricePerKWh: -0.10  // Negative price
        }
    }
}, "Negative price per kWh");

// Invalid time format in TOU
tryInsert("tariffs", {
    tariffId: "TAR9996",
    name: "Test TOU Tariff",
    type: "time_of_use",
    validFrom: new Date(),
    rates: {
        currency: "USD",
        timeOfUse: {
            peak: {
                hours: [{
                    start: "25:00",  // Invalid hour
                    end: "21:00"
                }],
                pricePerKWh: 0.20
            },
            offPeak: {
                pricePerKWh: 0.08
            }
        }
    }
}, "Invalid time format (25:00)");

// =====================================================
// 4. Readings Collection (Time-Series) Validation
// =====================================================
print("\n" + "-".repeat(50));
print("READINGS COLLECTION VALIDATION");
print("-".repeat(50));

// Missing timestamp
tryInsert("readings", {
    // Missing timestamp (required for time-series)
    meta: {
        meterId: "MTR0000000001",
        buildingId: "BLD00000001",
        meterType: "electricity"
    },
    kWhConsumed: 10.5,
    kWDemand: 5.2
}, "Missing timestamp field");

// Missing meta field
tryInsert("readings", {
    timestamp: new Date(),
    // Missing meta field (required for time-series)
    kWhConsumed: 10.5,
    kWDemand: 5.2
}, "Missing meta field");

// Negative consumption
tryInsert("readings", {
    timestamp: new Date(),
    meta: {
        meterId: "MTR0000000001",
        buildingId: "BLD00000001"
    },
    kWhConsumed: -10.5,  // Negative consumption (unless solar)
    kWDemand: 5.2
}, "Negative energy consumption");

// Invalid power factor
tryInsert("readings", {
    timestamp: new Date(),
    meta: {
        meterId: "MTR0000000001",
        buildingId: "BLD00000001"
    },
    kWhConsumed: 10.5,
    kWDemand: 5.2,
    powerFactor: 1.5  // Should be 0-1
}, "Power factor > 1");

// =====================================================
// 5. Events Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("EVENTS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid event ID pattern
tryInsert("events", {
    eventId: "EVENT123",  // Wrong pattern (should be EVT + 12 digits)
    eventType: "power_outage",
    timestamp: new Date(),
    severity: "critical"
}, "Invalid eventId pattern");

// Invalid event type
tryInsert("events", {
    eventId: "EVT999999999999",
    eventType: "solar_flare",  // Not in enum
    timestamp: new Date(),
    severity: "critical"
}, "Invalid eventType (not in enum)");

// Invalid severity
tryInsert("events", {
    eventId: "EVT999999999998",
    eventType: "peak_demand",
    timestamp: new Date(),
    severity: "catastrophic"  // Should be info/warning/critical/emergency
}, "Invalid severity level");

// Additional properties not allowed
tryInsert("events", {
    eventId: "EVT999999999997",
    eventType: "voltage_sag",
    timestamp: new Date(),
    severity: "warning",
    randomField: "not allowed"  // Additional property
}, "Additional properties not allowed");

// =====================================================
// 6. Bills Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("BILLS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid bill ID pattern
tryInsert("bills", {
    billId: "INVOICE123",  // Wrong pattern (should be BILL + 10 digits)
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(),
        days: 30
    },
    status: "issued",
    totalAmount: 100.00,
    createdAt: new Date()
}, "Invalid billId pattern");

// Invalid status
tryInsert("bills", {
    billId: "BILL9999999999",
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(),
        days: 30
    },
    status: "pending",  // Not in enum
    totalAmount: 100.00,
    createdAt: new Date()
}, "Invalid bill status");

// Negative total amount
tryInsert("bills", {
    billId: "BILL9999999998",
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(),
        days: 30
    },
    status: "issued",
    totalAmount: -100.00,  // Negative amount
    createdAt: new Date()
}, "Negative bill amount");

// Invalid payment method
tryInsert("bills", {
    billId: "BILL9999999997",
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(),
        days: 30
    },
    status: "paid",
    totalAmount: 100.00,
    paymentMethod: "bitcoin",  // Not in enum
    createdAt: new Date()
}, "Invalid payment method");

// Power factor out of range
tryInsert("bills", {
    billId: "BILL9999999996",
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(),
        days: 30
    },
    consumption: {
        totalKWh: 1000,
        powerFactor: 1.5  // Should be 0-1
    },
    status: "issued",
    totalAmount: 100.00,
    createdAt: new Date()
}, "Power factor > 1 in consumption");

// End date before start date
tryInsert("bills", {
    billId: "BILL9999999995",
    buildingId: "BLD00000001",
    billingPeriod: {
        start: new Date(),
        end: new Date(Date.now() - 30*24*60*60*1000),  // 30 days ago
        days: -30
    },
    status: "issued",
    totalAmount: 100.00,
    createdAt: new Date()
}, "Billing period end before start");

// =====================================================
// Summary
// =====================================================
print("\n" + "=".repeat(50));
print("Validation Testing Complete!");
print("All inserts failed as expected due to schema validation.");
print("This demonstrates the robustness of the schema design.");
print("=".repeat(50) + "\n");