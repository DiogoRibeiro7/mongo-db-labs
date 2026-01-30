// =====================================================
// Soil Humidity LoRaWAN - Schema Validation Testing
// File: 04_bad_inserts.js
// Purpose: Demonstrate schema validation with invalid documents
// Usage: mongosh mongodb://localhost:27017/lorawan_db 04_bad_inserts.js
// =====================================================

// Switch to the correct database
db = db.getSiblingDB('lorawan_db');

print('\n' + '='.repeat(60));
print('SCHEMA VALIDATION TESTING - Agricultural IoT');
print('='.repeat(60));
print('Testing LoRaWAN sensor data validation rules.\n');

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

        if (error.errInfo && error.errInfo.details) {
            print(`Validation Details: ${JSON.stringify(error.errInfo.details, null, 2)}`);
        }
    }
    print('-'.repeat(60));
}

// =====================================================
// FARMS COLLECTION - Invalid Inserts
// =====================================================
print('\n### FARMS COLLECTION VALIDATION ###\n');

// Test 1: Missing required farmName
tryInvalidInsert('farms', {
    farmId: 'FARM999',
    location: {
        type: 'Point',
        coordinates: [-120.5, 35.5]
    },
    totalAreaHa: 50.0
}, 'Missing required field: farmName');

// Test 2: Invalid area (negative)
tryInvalidInsert('farms', {
    farmId: 'FARM999',
    farmName: 'Invalid Farm',
    location: {
        type: 'Point',
        coordinates: [-120.5, 35.5]
    },
    totalAreaHa: -10.0  // Negative area not allowed
}, 'Invalid area: negative hectares');

// Test 3: Invalid GeoJSON type
tryInvalidInsert('farms', {
    farmId: 'FARM999',
    farmName: 'Bad Geo Farm',
    location: {
        type: 'LineString',  // Should be Point or Polygon
        coordinates: [[-120.5, 35.5], [-120.6, 35.6]]
    },
    totalAreaHa: 50.0
}, 'Invalid GeoJSON type (not Point or Polygon)');

// Test 4: Coordinates out of valid range
tryInvalidInsert('farms', {
    farmId: 'FARM999',
    farmName: 'Out of Bounds Farm',
    location: {
        type: 'Point',
        coordinates: [-200.0, 35.5]  // Longitude must be -180 to 180
    },
    totalAreaHa: 50.0
}, 'Invalid coordinates: longitude out of range');

// =====================================================
// FIELDS COLLECTION - Invalid Inserts
// =====================================================
print('\n### FIELDS COLLECTION VALIDATION ###\n');

// Test 5: Invalid crop type
tryInvalidInsert('fields', {
    fieldId: 'FIELD999',
    farmId: 'FARM001',
    fieldName: 'Test Field',
    cropType: 'bananas',  // Not in allowed crop list
    areaHa: 10.0,
    plantedDate: new Date()
}, 'Invalid enum value: crop type not allowed');

// Test 6: Area exceeding maximum
tryInvalidInsert('fields', {
    fieldId: 'FIELD999',
    farmId: 'FARM001',
    fieldName: 'Huge Field',
    cropType: 'corn',
    areaHa: 5000.0,  // Exceeds reasonable field size
    plantedDate: new Date()
}, 'Invalid area: exceeds maximum field size');

// Test 7: Invalid date (future planting)
tryInvalidInsert('fields', {
    fieldId: 'FIELD999',
    farmId: 'FARM001',
    fieldName: 'Future Field',
    cropType: 'wheat',
    areaHa: 10.0,
    plantedDate: new Date('2030-01-01')  // Future date
}, 'Invalid date: planted date in future');

// =====================================================
// GATEWAYS COLLECTION - Invalid Inserts
// =====================================================
print('\n### GATEWAYS COLLECTION VALIDATION ###\n');

// Test 8: Invalid gateway EUI format
tryInvalidInsert('gateways', {
    gatewayEui: 'INVALID',  // Should be 16 hex characters
    farmId: 'FARM001',
    model: 'RAK7244',
    location: {
        type: 'Point',
        coordinates: [-120.5, 35.5]
    }
}, 'Invalid EUI format (not 16 hex characters)');

// Test 9: Invalid model
tryInvalidInsert('gateways', {
    gatewayEui: 'A840411234567890',
    farmId: 'FARM001',
    model: 'UnknownModel',  // Not in allowed models list
    location: {
        type: 'Point',
        coordinates: [-120.5, 35.5]
    }
}, 'Invalid gateway model');

// Test 10: Missing location
tryInvalidInsert('gateways', {
    gatewayEui: 'A840411234567890',
    farmId: 'FARM001',
    model: 'RAK7244'
}, 'Missing required field: location');

// =====================================================
// DEVICES COLLECTION - Invalid Inserts
// =====================================================
print('\n### DEVICES COLLECTION VALIDATION ###\n');

// Test 11: Invalid device EUI
tryInvalidInsert('devices', {
    deviceEui: '12345',  // Too short
    fieldId: 'FIELD001',
    deviceType: 'soil_moisture',
    installDate: new Date()
}, 'Invalid device EUI (wrong length)');

// Test 12: Invalid spreading factor
tryInvalidInsert('devices', {
    deviceEui: 'D840411234567890',
    fieldId: 'FIELD001',
    deviceType: 'soil_moisture',
    loraConfig: {
        spreadingFactor: 13,  // Must be 7-12
        bandwidth: 125
    },
    installDate: new Date()
}, 'Invalid LoRa spreading factor (must be 7-12)');

// Test 13: Invalid bandwidth
tryInvalidInsert('devices', {
    deviceEui: 'D840411234567890',
    fieldId: 'FIELD001',
    deviceType: 'soil_moisture',
    loraConfig: {
        spreadingFactor: 10,
        bandwidth: 200  // Must be 125, 250, or 500
    },
    installDate: new Date()
}, 'Invalid LoRa bandwidth');

// =====================================================
// MEASUREMENTS COLLECTION - Invalid Inserts
// =====================================================
print('\n### MEASUREMENTS COLLECTION (Time-Series) ###\n');

// Test 14: Missing timestamp
tryInvalidInsert('measurements', {
    deviceEui: 'D840411234567890',
    soilMoisturePct: 45.0,
    temperatureC: 22.5
}, 'Missing required timestamp field');

// Test 15: Invalid soil moisture (> 100%)
tryInvalidInsert('measurements', {
    ts: new Date(),
    deviceEui: 'D840411234567890',
    soilMoisturePct: 150.0,  // Cannot exceed 100%
    temperatureC: 22.5
}, 'Invalid soil moisture: > 100%');

// Test 16: Invalid temperature (extreme)
tryInvalidInsert('measurements', {
    ts: new Date(),
    deviceEui: 'D840411234567890',
    soilMoisturePct: 45.0,
    temperatureC: 100.0  // Unrealistic for soil
}, 'Invalid temperature: extreme value');

// Test 17: Invalid RSSI value
tryInvalidInsert('measurements', {
    ts: new Date(),
    deviceEui: 'D840411234567890',
    soilMoisturePct: 45.0,
    rssi: 50  // RSSI should be negative
}, 'Invalid RSSI: must be negative');

// =====================================================
// IRRIGATION_SCHEDULES COLLECTION - Invalid Inserts
// =====================================================
print('\n### IRRIGATION SCHEDULES VALIDATION ###\n');

// Test 18: Invalid schedule type
tryInvalidInsert('irrigation_schedules', {
    scheduleId: 'SCH999',
    fieldId: 'FIELD001',
    scheduleType: 'random',  // Not a valid type
    enabled: true,
    parameters: {}
}, 'Invalid schedule type');

// Test 19: Invalid moisture thresholds
tryInvalidInsert('irrigation_schedules', {
    scheduleId: 'SCH999',
    fieldId: 'FIELD001',
    scheduleType: 'moisture_based',
    enabled: true,
    parameters: {
        minMoisturePct: 60,  // Min > Max (invalid)
        maxMoisturePct: 40
    }
}, 'Invalid moisture thresholds: min > max');

// Test 20: Invalid time format
tryInvalidInsert('irrigation_schedules', {
    scheduleId: 'SCH999',
    fieldId: 'FIELD001',
    scheduleType: 'time_based',
    enabled: true,
    parameters: {
        startTime: '25:00',  // Invalid hour
        durationMin: 30
    }
}, 'Invalid time format: hour out of range');

// =====================================================
// ALERTS COLLECTION - Invalid Inserts
// =====================================================
print('\n### ALERTS VALIDATION ###\n');

// Test 21: Invalid alert type
tryInvalidInsert('alerts', {
    alertId: 'ALT999',
    fieldId: 'FIELD001',
    alertType: 'unknown_alert',  // Not in enum
    severity: 'high',
    message: 'Test alert',
    triggeredAt: new Date()
}, 'Invalid alert type');

// Test 22: Invalid severity
tryInvalidInsert('alerts', {
    alertId: 'ALT999',
    fieldId: 'FIELD001',
    alertType: 'low_moisture',
    severity: 'extreme',  // Should be low/medium/high
    message: 'Test alert',
    triggeredAt: new Date()
}, 'Invalid severity level');

// Test 23: Message too short
tryInvalidInsert('alerts', {
    alertId: 'ALT999',
    fieldId: 'FIELD001',
    alertType: 'low_moisture',
    severity: 'high',
    message: 'Bad',  // Too short (min 5 chars)
    triggeredAt: new Date()
}, 'Invalid message: too short');

// =====================================================
// SUMMARY
// =====================================================
print('\n' + '='.repeat(60));
print('VALIDATION TESTING COMPLETE');
print('='.repeat(60));
print('\nKey Agricultural IoT Validation Rules:');
print('1. Farm areas must be positive');
print('2. Crop types from allowed list only');
print('3. LoRa parameters within spec (SF 7-12, BW 125/250/500)');
print('4. Soil moisture 0-100%');
print('5. Temperature within realistic ranges');
print('6. RSSI values must be negative');
print('7. EUI formats must be valid hex');
print('8. GeoJSON must follow standards');
print('9. Timestamps required for time-series');
print('10. Alert severity levels enforced');
print('\nNOTE: If any inserts succeeded unexpectedly, check that');
print('schema validation is enabled on your collections.');
print('Run 00_setup_mongodb.js to apply schemas.\n');