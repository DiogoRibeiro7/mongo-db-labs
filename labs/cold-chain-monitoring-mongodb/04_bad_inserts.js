// =====================================================
// Cold Chain Monitoring - Bad Inserts (Validation Demo)
// Demonstrates schema validation errors
// =====================================================

const dbName = "coldchain_db";
const db = db.getSiblingDB(dbName);

print("\nCold Chain Monitoring - Schema Validation Examples");
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
// 1. Assets Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("ASSETS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid asset ID pattern
tryInsert("assets", {
    assetId: "INVALID123",  // Wrong pattern (should be FRG/FRZ/TRK/CTN + 6 digits)
    assetType: "refrigerator",
    name: "Test Fridge",
    status: "active",
    location: {
        type: "Point",
        coordinates: [-73.935242, 40.730610],
        address: "Test Address"
    },
    temperatureRange: {
        min: 2.0,
        max: 8.0,
        optimal: 5.0
    },
    createdAt: new Date()
}, "Invalid assetId pattern");

// Invalid asset type
tryInsert("assets", {
    assetId: "FRG000001",
    assetType: "airplane",  // Not in enum
    name: "Test Asset",
    status: "active",
    location: {
        type: "Point",
        coordinates: [-73.935242, 40.730610],
        address: "Test Address"
    },
    temperatureRange: {
        min: 2.0,
        max: 8.0,
        optimal: 5.0
    },
    createdAt: new Date()
}, "Invalid assetType (not in enum)");

// Temperature range violation (min > max)
tryInsert("assets", {
    assetId: "FRZ000001",
    assetType: "freezer",
    name: "Test Freezer",
    status: "active",
    location: {
        type: "Point",
        coordinates: [-73.935242, 40.730610],
        address: "Test Address"
    },
    temperatureRange: {
        min: 10.0,  // Min greater than max
        max: 5.0,
        optimal: 7.0
    },
    createdAt: new Date()
}, "Invalid temperature range (min > max)");

// Invalid coordinates (longitude out of range)
tryInsert("assets", {
    assetId: "TRK000001",
    assetType: "truck",
    name: "Test Truck",
    status: "active",
    location: {
        type: "Point",
        coordinates: [200, 40.730610],  // Longitude > 180
        address: "Test Address"
    },
    temperatureRange: {
        min: -20.0,
        max: -10.0,
        optimal: -15.0
    },
    createdAt: new Date()
}, "Invalid longitude (>180)");

// Missing required field
tryInsert("assets", {
    assetId: "CTN000001",
    assetType: "container",
    // Missing 'name' field
    status: "active",
    location: {
        type: "Point",
        coordinates: [-73.935242, 40.730610],
        address: "Test Address"
    },
    temperatureRange: {
        min: 2.0,
        max: 8.0,
        optimal: 5.0
    },
    createdAt: new Date()
}, "Missing required field 'name'");

// =====================================================
// 2. Sensors Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("SENSORS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid sensor ID pattern
tryInsert("sensors", {
    sensorId: "SENSOR123",  // Wrong pattern (should be SEN + 8 digits)
    assetId: "FRG000001",
    sensorType: "temperature",
    status: "active",
    installedAt: new Date()
}, "Invalid sensorId pattern");

// Invalid sensor type
tryInsert("sensors", {
    sensorId: "SEN00000001",
    assetId: "FRG000001",
    sensorType: "pressure",  // Not in enum
    status: "active",
    installedAt: new Date()
}, "Invalid sensorType (not in enum)");

// Battery level out of range
tryInsert("sensors", {
    sensorId: "SEN00000002",
    assetId: "FRZ000001",
    sensorType: "humidity",
    status: "active",
    batteryLevel: 150,  // Max is 100
    installedAt: new Date()
}, "Battery level > 100");

// Invalid calibration offset
tryInsert("sensors", {
    sensorId: "SEN00000003",
    assetId: "TRK000001",
    sensorType: "temperature",
    status: "active",
    calibration: {
        offset: -15.0,  // Min is -10
        lastCalibrated: new Date()
    },
    installedAt: new Date()
}, "Calibration offset out of range");

// =====================================================
// 3. Measurements Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("MEASUREMENTS COLLECTION VALIDATION");
print("-".repeat(50));

// Temperature out of range
tryInsert("measurements", {
    timestamp: new Date(),
    meta: {
        assetId: "FRG000001",
        sensorId: "SEN00000001"
    },
    temperature: 100.0,  // Max is 50°C
    humidity: 50.0
}, "Temperature > 50°C (out of range)");

// Humidity out of range
tryInsert("measurements", {
    timestamp: new Date(),
    meta: {
        assetId: "FRZ000001",
        sensorId: "SEN00000002"
    },
    temperature: -20.0,
    humidity: 120.0  // Max is 100%
}, "Humidity > 100%");

// Invalid sampling mode
tryInsert("measurements", {
    timestamp: new Date(),
    meta: {
        assetId: "TRK000001",
        sensorId: "SEN00000003"
    },
    temperature: 5.0,
    samplingMode: "turbo"  // Not in enum
}, "Invalid sampling mode");

// Missing required meta fields
tryInsert("measurements", {
    timestamp: new Date(),
    meta: {
        assetId: "CTN000001"
        // Missing sensorId
    },
    temperature: 2.0
}, "Missing required meta.sensorId");

// Invalid signal strength
tryInsert("measurements", {
    timestamp: new Date(),
    meta: {
        assetId: "FRG000001",
        sensorId: "SEN00000001"
    },
    temperature: 5.0,
    signalStrength: 10  // Should be negative (dBm)
}, "Invalid signal strength (positive dBm)");

// =====================================================
// 4. Events Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("EVENTS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid event ID pattern
tryInsert("events", {
    eventId: "EVENT123",  // Wrong pattern (should be EVT + 10 digits)
    assetId: "FRG000001",
    eventType: "door_open",
    timestamp: new Date(),
    severity: "warning"
}, "Invalid eventId pattern");

// Invalid event type
tryInsert("events", {
    eventId: "EVT0000000001",
    assetId: "FRZ000001",
    eventType: "explosion",  // Not in enum
    timestamp: new Date(),
    severity: "critical"
}, "Invalid eventType (not in enum)");

// Invalid severity
tryInsert("events", {
    eventId: "EVT0000000002",
    assetId: "TRK000001",
    eventType: "power_failure",
    timestamp: new Date(),
    severity: "extreme"  // Should be info/warning/critical
}, "Invalid severity level");

// Additional properties not allowed
tryInsert("events", {
    eventId: "EVT0000000003",
    assetId: "CTN000001",
    eventType: "door_open",
    timestamp: new Date(),
    severity: "info",
    randomField: "not allowed"  // Additional property
}, "Additional properties not allowed");

// =====================================================
// 5. Routes Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("ROUTES COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid route ID pattern
tryInsert("routes", {
    routeId: "ROUTE123",  // Wrong pattern (should be RT + 8 digits)
    assetId: "TRK000001",
    status: "in_progress",
    origin: {
        name: "Warehouse A",
        coordinates: [-73.935242, 40.730610]
    },
    destination: {
        name: "Store B",
        coordinates: [-74.006020, 40.712776]
    },
    startTime: new Date()
}, "Invalid routeId pattern");

// Invalid route status
tryInsert("routes", {
    routeId: "RT00000001",
    assetId: "TRK000001",
    status: "lost",  // Not in enum
    origin: {
        name: "Warehouse A",
        coordinates: [-73.935242, 40.730610]
    },
    destination: {
        name: "Store B",
        coordinates: [-74.006020, 40.712776]
    },
    startTime: new Date()
}, "Invalid route status");

// Missing required origin fields
tryInsert("routes", {
    routeId: "RT00000002",
    assetId: "CTN000001",
    status: "planned",
    origin: {
        name: "Warehouse A"
        // Missing coordinates
    },
    destination: {
        name: "Store B",
        coordinates: [-74.006020, 40.712776]
    },
    startTime: new Date()
}, "Missing origin coordinates");

// Invalid coordinates in waypoint
tryInsert("routes", {
    routeId: "RT00000003",
    assetId: "TRK000002",
    status: "in_progress",
    origin: {
        name: "Warehouse A",
        coordinates: [-73.935242, 40.730610]
    },
    destination: {
        name: "Store B",
        coordinates: [-74.006020, 40.712776]
    },
    waypoints: [{
        name: "Rest Stop",
        coordinates: [-73.950000, 100.0],  // Latitude > 90
        arrivalTime: new Date()
    }],
    startTime: new Date()
}, "Invalid waypoint latitude");

// =====================================================
// 6. Alerts Collection Validation Errors
// =====================================================
print("\n" + "-".repeat(50));
print("ALERTS COLLECTION VALIDATION");
print("-".repeat(50));

// Invalid alert ID pattern
tryInsert("alerts", {
    alertId: "ALERT123",  // Wrong pattern (should be ALT + 10 digits)
    assetId: "FRG000001",
    alertType: "temperature_high",
    severity: "high",
    status: "active",
    triggeredAt: new Date()
}, "Invalid alertId pattern");

// Invalid alert type
tryInsert("alerts", {
    alertId: "ALT0000000001",
    assetId: "FRZ000001",
    alertType: "fire_alarm",  // Not in enum
    severity: "critical",
    status: "active",
    triggeredAt: new Date()
}, "Invalid alertType (not in enum)");

// Invalid severity
tryInsert("alerts", {
    alertId: "ALT0000000002",
    assetId: "TRK000001",
    alertType: "battery_low",
    severity: "minor",  // Should be low/medium/high/critical
    status: "active",
    triggeredAt: new Date()
}, "Invalid severity level");

// Invalid alert status
tryInsert("alerts", {
    alertId: "ALT0000000003",
    assetId: "CTN000001",
    alertType: "door_open_too_long",
    severity: "medium",
    status: "ignored",  // Should be active/acknowledged/resolved/escalated
    triggeredAt: new Date()
}, "Invalid alert status");

// Invalid threshold operator
tryInsert("alerts", {
    alertId: "ALT0000000004",
    assetId: "FRG000002",
    alertType: "temperature_high",
    severity: "high",
    status: "active",
    threshold: {
        metric: "temperature",
        operator: "between",  // Not a valid operator
        value: 10.0,
        duration: 300
    },
    triggeredAt: new Date()
}, "Invalid threshold operator");

// Message too long
tryInsert("alerts", {
    alertId: "ALT0000000005",
    assetId: "FRZ000002",
    alertType: "humidity_high",
    severity: "low",
    status: "active",
    message: "x".repeat(501),  // Max length is 500
    triggeredAt: new Date()
}, "Message exceeds 500 characters");

// =====================================================
// Summary
// =====================================================
print("\n" + "=".repeat(50));
print("Validation Testing Complete!");
print("All inserts failed as expected due to schema validation.");
print("This demonstrates the robustness of the schema design.");
print("=".repeat(50) + "\n");