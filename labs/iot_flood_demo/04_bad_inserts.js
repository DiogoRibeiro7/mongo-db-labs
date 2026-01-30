// =====================================================
// IoT Flood Demo - Schema Validation Testing
// File: 04_bad_inserts.js
// Purpose: Demonstrate schema validation with invalid documents
// Usage: mongosh mongodb://localhost:27017/iot_flood_demo 04_bad_inserts.js
// =====================================================

// Switch to the correct database
db = db.getSiblingDB('iot_flood_demo');

print('\n' + '='.repeat(60));
print('SCHEMA VALIDATION TESTING - Invalid Document Examples');
print('='.repeat(60));
print('Each test will attempt an invalid insert and show the error.\n');

// Helper function to attempt insert and display result
function tryInvalidInsert(collection, document, description) {
    print(`\n[TEST] ${description}`);
    print(`Collection: ${collection}`);
    print(`Document: ${JSON.stringify(document, null, 2)}`);

    try {
        db[collection].insertOne(document);
        print(`❌ UNEXPECTED: Insert succeeded (validation may be disabled)`);
    } catch (error) {
        print(`✅ EXPECTED: Validation error occurred`);
        print(`Error: ${error.message}`);

        // Extract validation details if available
        if (error.errInfo && error.errInfo.details) {
            print(`Validation Details: ${JSON.stringify(error.errInfo.details, null, 2)}`);
        }
    }
    print('-'.repeat(60));
}

// =====================================================
// SITES COLLECTION - Invalid Inserts
// =====================================================
print('\n### SITES COLLECTION VALIDATION ###\n');

// Test 1: Missing required field (siteName)
tryInvalidInsert('sites', {
    siteId: 'INVALID_001',
    location: { lat: 45.5, lon: -122.6 },
    installDate: new Date()
}, 'Missing required field: siteName');

// Test 2: Invalid location coordinates (lat out of range)
tryInvalidInsert('sites', {
    siteId: 'INVALID_002',
    siteName: 'Invalid Location Site',
    location: { lat: 200.0, lon: -122.6 },  // lat must be -90 to 90
    installDate: new Date()
}, 'Invalid latitude (out of range: -90 to 90)');

// Test 3: Wrong data type for installDate
tryInvalidInsert('sites', {
    siteId: 'INVALID_003',
    siteName: 'Wrong Date Type',
    location: { lat: 45.5, lon: -122.6 },
    installDate: '2024-01-01'  // Should be Date, not string
}, 'Wrong data type: installDate as string instead of Date');

// Test 4: Additional unexpected properties
tryInvalidInsert('sites', {
    siteId: 'INVALID_004',
    siteName: 'Extra Properties Site',
    location: { lat: 45.5, lon: -122.6 },
    installDate: new Date(),
    unexpectedField: 'This should not be allowed',
    anotherBadField: 123
}, 'Additional properties not allowed');

// =====================================================
// SENSORS COLLECTION - Invalid Inserts
// =====================================================
print('\n### SENSORS COLLECTION VALIDATION ###\n');

// Test 5: Invalid sensorType enum value
tryInvalidInsert('sensors', {
    sensorId: 'INVALID_SENSOR_001',
    siteId: 'SITE001',
    sensorType: 'INVALID_TYPE',  // Not in enum
    installDate: new Date(),
    isActive: true
}, 'Invalid enum value for sensorType');

// Test 6: Missing required siteId reference
tryInvalidInsert('sensors', {
    sensorId: 'INVALID_SENSOR_002',
    sensorType: 'water_level',
    installDate: new Date(),
    isActive: true
}, 'Missing required field: siteId');

// Test 7: Invalid boolean type
tryInvalidInsert('sensors', {
    sensorId: 'INVALID_SENSOR_003',
    siteId: 'SITE001',
    sensorType: 'water_level',
    installDate: new Date(),
    isActive: 'yes'  // Should be boolean, not string
}, 'Wrong data type: isActive as string instead of boolean');

// =====================================================
// MEASUREMENTS COLLECTION - Invalid Inserts
// =====================================================
print('\n### MEASUREMENTS COLLECTION (Time-Series) ###\n');

// Test 8: Missing timestamp field
tryInvalidInsert('measurements', {
    sensorId: 'WL001',
    waterLevelM: 2.5,
    batteryV: 3.7
}, 'Missing required timestamp field (ts)');

// Test 9: Negative water level
tryInvalidInsert('measurements', {
    ts: new Date(),
    sensorId: 'WL001',
    waterLevelM: -5.0,  // Water level can't be negative
    batteryV: 3.7
}, 'Invalid metric: negative water level');

// Test 10: Battery voltage out of range
tryInvalidInsert('measurements', {
    ts: new Date(),
    sensorId: 'WL001',
    waterLevelM: 2.5,
    batteryV: 10.0  // Battery voltage typically 0-5V
}, 'Battery voltage out of expected range (0-5V)');

// Test 11: Wrong timestamp type
tryInvalidInsert('measurements', {
    ts: Date.now(),  // Number instead of Date
    sensorId: 'WL001',
    waterLevelM: 2.5,
    batteryV: 3.7
}, 'Wrong data type: timestamp as number instead of Date');

// =====================================================
// SAMPLING POLICIES COLLECTION - Invalid Inserts
// =====================================================
print('\n### SAMPLING POLICIES VALIDATION ###\n');

// Test 12: Invalid schedule format
tryInvalidInsert('samplingPolicies', {
    policyId: 'INVALID_POLICY_001',
    policyName: 'Bad Schedule Policy',
    isActive: true,
    baseIntervalMin: -10,  // Negative interval not allowed
    conditions: []
}, 'Invalid schedule: negative interval');

// Test 13: Missing required conditions array
tryInvalidInsert('samplingPolicies', {
    policyId: 'INVALID_POLICY_002',
    policyName: 'No Conditions Policy',
    isActive: true,
    baseIntervalMin: 15
}, 'Missing required field: conditions array');

// Test 14: Invalid condition operator
tryInvalidInsert('samplingPolicies', {
    policyId: 'INVALID_POLICY_003',
    policyName: 'Bad Operator Policy',
    isActive: true,
    baseIntervalMin: 15,
    conditions: [{
        metric: 'waterLevelM',
        operator: 'INVALID_OP',  // Not a valid operator
        threshold: 2.0,
        action: 'increase_frequency'
    }]
}, 'Invalid enum value: condition operator');

// =====================================================
// ALERTS COLLECTION - Invalid Inserts
// =====================================================
print('\n### ALERTS VALIDATION ###\n');

// Test 15: Invalid severity level
tryInvalidInsert('alerts', {
    alertId: 'INVALID_ALERT_001',
    siteId: 'SITE001',
    sensorId: 'WL001',
    alertType: 'high_water',
    severity: 'SUPER_CRITICAL',  // Not in enum: info, warning, critical
    message: 'Test alert',
    triggeredAt: new Date(),
    isAcknowledged: false
}, 'Invalid enum value: severity level');

// Test 16: Missing message for alert
tryInvalidInsert('alerts', {
    alertId: 'INVALID_ALERT_002',
    siteId: 'SITE001',
    sensorId: 'WL001',
    alertType: 'sensor_offline',
    severity: 'warning',
    triggeredAt: new Date(),
    isAcknowledged: false
}, 'Missing required field: message');

// Test 17: Invalid acknowledgment structure
tryInvalidInsert('alerts', {
    alertId: 'INVALID_ALERT_003',
    siteId: 'SITE001',
    sensorId: 'WL001',
    alertType: 'battery_low',
    severity: 'info',
    message: 'Low battery detected',
    triggeredAt: new Date(),
    isAcknowledged: 'not yet'  // Should be boolean
}, 'Wrong data type: isAcknowledged as string');

// =====================================================
// RATING CURVES COLLECTION - Invalid Inserts
// =====================================================
print('\n### RATING CURVES VALIDATION ###\n');

// Test 18: Empty data points array
tryInvalidInsert('ratingCurves', {
    curveId: 'INVALID_CURVE_001',
    siteId: 'SITE001',
    validFrom: new Date(),
    dataPoints: []  // Must have at least 2 points
}, 'Invalid rating curve: empty data points');

// Test 19: Non-monotonic data points
tryInvalidInsert('ratingCurves', {
    curveId: 'INVALID_CURVE_002',
    siteId: 'SITE001',
    validFrom: new Date(),
    dataPoints: [
        { levelM: 1.0, flowM3s: 10.0 },
        { levelM: 0.5, flowM3s: 20.0 },  // Level decreases but flow increases
        { levelM: 2.0, flowM3s: 30.0 }
    ]
}, 'Invalid rating curve: non-monotonic data');

// Test 20: Negative flow values
tryInvalidInsert('ratingCurves', {
    curveId: 'INVALID_CURVE_003',
    siteId: 'SITE001',
    validFrom: new Date(),
    dataPoints: [
        { levelM: 0.0, flowM3s: -5.0 },  // Negative flow not physical
        { levelM: 1.0, flowM3s: 10.0 }
    ]
}, 'Invalid metric: negative flow rate');

// =====================================================
// SUMMARY
// =====================================================
print('\n' + '='.repeat(60));
print('VALIDATION TESTING COMPLETE');
print('='.repeat(60));
print('\nKey Validation Rules Demonstrated:');
print('1. Required fields must be present');
print('2. Data types must match schema definitions');
print('3. Enum values must be from allowed list');
print('4. Numeric ranges must be respected');
print('5. Additional properties may be rejected');
print('6. Timestamp fields require Date objects');
print('7. Reference fields must follow conventions');
print('8. Arrays cannot be empty when required');
print('\nNOTE: If any inserts succeeded unexpectedly, check that');
print('schema validation is enabled on your collections.');
print('Run 00_setup_mongodb.js to apply schemas.\n');