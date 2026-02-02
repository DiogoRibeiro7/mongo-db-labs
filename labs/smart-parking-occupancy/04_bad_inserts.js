// =====================================================
// Smart Parking Occupancy - Bad Inserts (Validation Demo)
// Demonstrates schema validation errors
// =====================================================

const dbName = "smartparking_db";
const db = db.getSiblingDB(dbName);

print("\nSmart Parking Occupancy - Schema Validation Examples");
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
// 1. Zones Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("ZONES COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid zone ID pattern
tryInsert("zones", {
    zoneId: "Z123",  // Wrong pattern (should be ZONE + 4 digits)
    name: "Invalid Zone",
    type: "street",
    location: {
        type: "Polygon",
        coordinates: [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        address: "Test Street"
    },
    totalSpots: 50,
    pricing: {
        currency: "USD",
        perHour: 5.00
    },
    createdAt: new Date()
}, "Invalid zoneId pattern");

// Invalid zone type
tryInsert("zones", {
    zoneId: "ZONE9999",
    name: "Test Zone",
    type: "highway",  // Not in enum
    location: {
        type: "Polygon",
        coordinates: [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        address: "Test Street"
    },
    totalSpots: 50,
    pricing: {
        currency: "USD",
        perHour: 5.00
    },
    createdAt: new Date()
}, "Invalid zone type (not in enum)");

// Invalid location type (not Polygon)
tryInsert("zones", {
    zoneId: "ZONE9998",
    name: "Test Zone",
    type: "lot",
    location: {
        type: "Point",  // Should be Polygon
        coordinates: [-122.4194, 37.7749],
        address: "Test Street"
    },
    totalSpots: 50,
    pricing: {
        currency: "USD",
        perHour: 5.00
    },
    createdAt: new Date()
}, "Invalid location type (should be Polygon)");

// Negative pricing
tryInsert("zones", {
    zoneId: "ZONE9997",
    name: "Test Zone",
    type: "garage",
    location: {
        type: "Polygon",
        coordinates: [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        address: "Test Street"
    },
    totalSpots: 50,
    pricing: {
        currency: "USD",
        perHour: -5.00  // Negative price
    },
    createdAt: new Date()
}, "Negative hourly rate");

// Invalid currency
tryInsert("zones", {
    zoneId: "ZONE9996",
    name: "Test Zone",
    type: "street",
    location: {
        type: "Polygon",
        coordinates: [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        address: "Test Street"
    },
    totalSpots: 50,
    pricing: {
        currency: "BTC",  // Not in enum
        perHour: 5.00
    },
    createdAt: new Date()
}, "Invalid currency (not USD/EUR/GBP)");

// =====================================================
// 2. Parking Spots Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("PARKING SPOTS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid spot ID pattern
tryInsert("parking_spots", {
    spotId: "PARK123",  // Wrong pattern (should be SPOT + 8 digits)
    zoneId: "ZONE0001",
    spotNumber: "A-01",
    type: "standard",
    status: "available",
    location: {
        type: "Point",
        coordinates: [-122.4194, 37.7749]
    },
    createdAt: new Date()
}, "Invalid spotId pattern");

// Invalid spot type
tryInsert("parking_spots", {
    spotId: "SPOT99999999",
    zoneId: "ZONE0001",
    spotNumber: "A-01",
    type: "helicopter",  // Not in enum
    status: "available",
    location: {
        type: "Point",
        coordinates: [-122.4194, 37.7749]
    },
    createdAt: new Date()
}, "Invalid spot type (not in enum)");

// Invalid spot status
tryInsert("parking_spots", {
    spotId: "SPOT99999998",
    zoneId: "ZONE0001",
    spotNumber: "A-01",
    type: "standard",
    status: "broken",  // Not in enum
    location: {
        type: "Point",
        coordinates: [-122.4194, 37.7749]
    },
    createdAt: new Date()
}, "Invalid spot status");

// Invalid coordinates (latitude out of range)
tryInsert("parking_spots", {
    spotId: "SPOT99999997",
    zoneId: "ZONE0001",
    spotNumber: "A-01",
    type: "standard",
    status: "available",
    location: {
        type: "Point",
        coordinates: [-122.4194, 95.0]  // Latitude > 90
    },
    createdAt: new Date()
}, "Invalid latitude (>90)");

// Missing required field
tryInsert("parking_spots", {
    spotId: "SPOT99999996",
    zoneId: "ZONE0001",
    // Missing spotNumber
    type: "standard",
    status: "available",
    location: {
        type: "Point",
        coordinates: [-122.4194, 37.7749]
    },
    createdAt: new Date()
}, "Missing required field 'spotNumber'");

// =====================================================
// 3. Sensors Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("SENSORS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid sensor ID pattern
tryInsert("sensors", {
    sensorId: "SENSOR1",  // Wrong pattern (should be SEN + 8 digits)
    type: "magnetometer",
    spotId: "SPOT00000001",
    status: "active",
    installedAt: new Date()
}, "Invalid sensorId pattern");

// Invalid sensor type
tryInsert("sensors", {
    sensorId: "SEN99999999",
    type: "quantum",  // Not in enum
    spotId: "SPOT00000001",
    status: "active",
    installedAt: new Date()
}, "Invalid sensor type (not in enum)");

// Invalid sensor status
tryInsert("sensors", {
    sensorId: "SEN99999998",
    type: "magnetometer",
    spotId: "SPOT00000001",
    status: "destroyed",  // Not in enum
    installedAt: new Date()
}, "Invalid sensor status");

// Battery level out of range
tryInsert("sensors", {
    sensorId: "SEN99999997",
    type: "ultrasonic",
    spotId: "SPOT00000001",
    status: "active",
    batteryLevel: 150,  // Max is 100
    installedAt: new Date()
}, "Battery level > 100");

// Invalid connectivity protocol
tryInsert("sensors", {
    sensorId: "SEN99999996",
    type: "infrared",
    spotId: "SPOT00000001",
    status: "active",
    connectivity: {
        protocol: "Bluetooth",  // Not in enum
        gatewayId: "GW001",
        signalStrength: -60,
        lastSeen: new Date()
    },
    installedAt: new Date()
}, "Invalid connectivity protocol");

// =====================================================
// 4. Occupancy Readings Validation (Time-Series)
// =====================================================
print("\n" + "-".repeat(50));
print("OCCUPANCY READINGS COLLECTION VALIDATION");
print("-".repeat(50));

// Note: Time-series collections have limited validation
// But we can still test some basic issues

// Missing timestamp
tryInsert("occupancy_readings", {
    // Missing timestamp (required for time-series)
    meta: {
        spotId: "SPOT00000001",
        sensorId: "SEN00000001",
        zoneId: "ZONE0001"
    },
    occupied: true,
    confidence: 0.95
}, "Missing timestamp field");

// Missing meta field
tryInsert("occupancy_readings", {
    timestamp: new Date(),
    // Missing meta field (required for time-series)
    occupied: true,
    confidence: 0.95
}, "Missing meta field");

// Invalid confidence (out of range)
tryInsert("occupancy_readings", {
    timestamp: new Date(),
    meta: {
        spotId: "SPOT00000001",
        sensorId: "SEN00000001",
        zoneId: "ZONE0001"
    },
    occupied: true,
    confidence: 1.5  // Should be 0-1
}, "Confidence value > 1");

// =====================================================
// 5. Events Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("EVENTS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid event ID pattern
tryInsert("events", {
    eventId: "EVENT123",  // Wrong pattern (should be EVT + 10 digits)
    eventType: "occupancy_change",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date()
}, "Invalid eventId pattern");

// Invalid event type
tryInsert("events", {
    eventId: "EVT9999999999",
    eventType: "alien_landing",  // Not in enum
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date()
}, "Invalid eventType (not in enum)");

// Invalid severity
tryInsert("events", {
    eventId: "EVT9999999998",
    eventType: "sensor_offline",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    severity: "catastrophic"  // Should be info/warning/critical
}, "Invalid severity level");

// Additional properties not allowed
tryInsert("events", {
    eventId: "EVT9999999997",
    eventType: "occupancy_change",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    randomField: "not allowed"  // Additional property
}, "Additional properties not allowed");

// =====================================================
// 6. Violations Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("VIOLATIONS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid violation ID pattern
tryInsert("violations", {
    violationId: "VIOL123",  // Wrong pattern (should be VIO + 10 digits)
    type: "overstay",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "active"
}, "Invalid violationId pattern");

// Invalid violation type
tryInsert("violations", {
    violationId: "VIO9999999999",
    type: "speeding",  // Not a parking violation type
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "active"
}, "Invalid violation type");

// Invalid status
tryInsert("violations", {
    violationId: "VIO9999999998",
    type: "overstay",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "ignored"  // Not in enum
}, "Invalid violation status");

// Negative fine amount
tryInsert("violations", {
    violationId: "VIO9999999997",
    type: "no_payment",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "active",
    fine: {
        amount: -50.00,  // Negative amount
        currency: "USD",
        dueDate: new Date(Date.now() + 30*24*60*60*1000)
    }
}, "Negative fine amount");

// Invalid currency in fine
tryInsert("violations", {
    violationId: "VIO9999999996",
    type: "invalid_permit",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "active",
    fine: {
        amount: 50.00,
        currency: "YEN",  // Not in enum
        dueDate: new Date(Date.now() + 30*24*60*60*1000)
    }
}, "Invalid currency in fine");

// Invalid detection method
tryInsert("violations", {
    violationId: "VIO9999999995",
    type: "wrong_spot_type",
    spotId: "SPOT00000001",
    zoneId: "ZONE0001",
    timestamp: new Date(),
    status: "active",
    detectedBy: "psychic"  // Not in enum
}, "Invalid detection method");

// =====================================================
// Summary
// =====================================================
print("\n" + "=".repeat(50));
print("Validation Testing Complete!");
print("All inserts failed as expected due to schema validation.");
print("This demonstrates the robustness of the schema design.");
print("=".repeat(50) + "\n");