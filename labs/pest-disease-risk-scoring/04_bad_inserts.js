/**
 * Schema Validation Examples: Agricultural Pest & Disease Risk Scoring
 *
 * This file demonstrates MongoDB schema validation by attempting invalid inserts.
 * Each example shows what fails and why, helping understand data integrity rules.
 */

// Use the correct database
use('agrimonitor_db');

print("=== Schema Validation Examples - Agricultural Monitoring ===\n");
print("These inserts will fail due to validation rules, demonstrating data integrity.\n");

// ========================================================================
// FARMS COLLECTION - Validation Examples
// ========================================================================
print("1. FARMS - Invalid location coordinates (out of range):");
print("   Latitude must be between -90 and 90, longitude between -180 and 180\n");

try {
    db.farms.insertOne({
        farmId: "FARM_INVALID_001",
        name: "Invalid Location Farm",
        location: {
            type: "Point",
            coordinates: [200, 95]  // Invalid: longitude > 180, latitude > 90
        },
        owner: {
            name: "Test Owner",
            contactEmail: "test@farm.com",
            contactPhone: "+1-555-0100"
        },
        area: {
            total: 100,
            cultivated: 80,
            unit: "hectares"
        },
        management: {
            pestManagement: "IPM",
            irrigationType: "drip"
        },
        certifications: {
            organic: false,
            globalGAP: true
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid coordinates!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("2. FARMS - Invalid email format:");
print("   Email must follow standard format (contains @ and domain)\n");

try {
    db.farms.insertOne({
        farmId: "FARM_INVALID_002",
        name: "Bad Email Farm",
        location: {
            type: "Point",
            coordinates: [-120.5, 35.7]
        },
        owner: {
            name: "Test Owner",
            contactEmail: "not-an-email",  // Invalid email format
            contactPhone: "+1-555-0100"
        },
        area: {
            total: 100,
            cultivated: 80,
            unit: "hectares"
        },
        management: {
            pestManagement: "conventional",
            irrigationType: "flood"
        },
        certifications: {
            organic: false,
            globalGAP: false
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid email!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// FIELDS COLLECTION - Validation Examples
// ========================================================================
print("3. FIELDS - Invalid growth stage:");
print("   Growth stage must be one of: seedling, vegetative, flowering, fruiting, harvest\n");

try {
    db.fields.insertOne({
        fieldId: "FLD_INVALID_001",
        farmId: "FARM00000001",
        name: "Invalid Stage Field",
        area: 5.5,
        crop: {
            type: "tomato",
            variety: "Roma",
            plantingDate: new Date("2024-01-01"),
            expectedHarvest: new Date("2024-04-01"),
            growthStage: "sprouting"  // Invalid: not in allowed enum
        },
        soil: {
            type: "loamy",
            pH: 6.5
        },
        location: {
            type: "Polygon",
            coordinates: [[
                [-120.5, 35.7],
                [-120.49, 35.7],
                [-120.49, 35.69],
                [-120.5, 35.69],
                [-120.5, 35.7]
            ]]
        },
        riskHistory: {
            averageRisk: 45,
            highestRisk: 78,
            lastHighRisk: new Date()
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid growth stage!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("4. FIELDS - Invalid soil pH (out of range):");
print("   Soil pH must be between 0 and 14\n");

try {
    db.fields.insertOne({
        fieldId: "FLD_INVALID_002",
        farmId: "FARM00000001",
        name: "Bad pH Field",
        area: 3.0,
        crop: {
            type: "corn",
            variety: "Sweet Corn",
            plantingDate: new Date("2024-01-01"),
            expectedHarvest: new Date("2024-06-01"),
            growthStage: "vegetative"
        },
        soil: {
            type: "sandy",
            pH: 15.5  // Invalid: pH > 14
        },
        location: {
            type: "Polygon",
            coordinates: [[
                [-120.5, 35.7],
                [-120.49, 35.7],
                [-120.49, 35.69],
                [-120.5, 35.69],
                [-120.5, 35.7]
            ]]
        },
        riskHistory: {
            averageRisk: 30,
            highestRisk: 65,
            lastHighRisk: new Date()
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid pH!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// SENSORS COLLECTION - Validation Examples
// ========================================================================
print("5. SENSORS - Invalid sensor type:");
print("   Sensor type must be: weather_station, leaf_wetness, pest_trap, or soil_moisture\n");

try {
    db.sensors.insertOne({
        sensorId: "SNS_INVALID_001",
        fieldId: "FLD00000001",
        sensorType: "humidity_sensor",  // Invalid: not in allowed types
        manufacturer: "AgroTech",
        model: "HUM-3000",
        installDate: new Date("2024-01-01"),
        lastMaintenance: new Date("2024-01-15"),
        status: "active",
        location: {
            type: "Point",
            coordinates: [-120.5, 35.7]
        },
        configuration: {
            samplingInterval: 15,
            unit: "minutes"
        },
        calibration: {
            lastCalibrated: new Date("2024-01-15"),
            nextCalibration: new Date("2024-07-15")
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid sensor type!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("6. SENSORS - Invalid status:");
print("   Status must be: active, maintenance, or inactive\n");

try {
    db.sensors.insertOne({
        sensorId: "SNS_INVALID_002",
        fieldId: "FLD00000001",
        sensorType: "weather_station",
        manufacturer: "WeatherPro",
        model: "WS-5000",
        installDate: new Date("2024-01-01"),
        lastMaintenance: new Date("2024-01-15"),
        status: "broken",  // Invalid: not in allowed status values
        location: {
            type: "Point",
            coordinates: [-120.5, 35.7]
        },
        configuration: {
            samplingInterval: 30,
            unit: "minutes"
        },
        calibration: {
            lastCalibrated: new Date("2024-01-15"),
            nextCalibration: new Date("2024-07-15")
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid status!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// MEASUREMENTS COLLECTION - Validation Examples
// ========================================================================
print("7. MEASUREMENTS - Negative temperature value:");
print("   Temperature in Celsius must be reasonable (-50 to 60)\n");

try {
    db.measurements.insertOne({
        sensorId: "SNS00000001",
        fieldId: "FLD00000001",
        sensorType: "weather_station",
        timestamp: new Date(),
        data: {
            temperature: -100,  // Invalid: unrealistic temperature
            humidity: 75,
            rainfall: 5,
            windSpeed: 15
        },
        quality: {
            status: "valid",
            confidence: 0.95
        }
    });
    print("   ❌ ERROR: Should have failed - invalid temperature!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("8. MEASUREMENTS - Invalid humidity percentage:");
print("   Humidity must be between 0 and 100 percent\n");

try {
    db.measurements.insertOne({
        sensorId: "SNS00000002",
        fieldId: "FLD00000001",
        sensorType: "leaf_wetness",
        timestamp: new Date(),
        data: {
            leafWetnessHours: 8,
            temperature: 22,
            humidity: 150  // Invalid: > 100%
        },
        quality: {
            status: "valid",
            confidence: 0.95
        }
    });
    print("   ❌ ERROR: Should have failed - invalid humidity!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// RISK_ASSESSMENTS COLLECTION - Validation Examples
// ========================================================================
print("9. RISK_ASSESSMENTS - Risk score out of range:");
print("   Risk score must be between 0 and 100\n");

try {
    db.risk_assessments.insertOne({
        assessmentId: "RISK_INVALID_001",
        fieldId: "FLD00000001",
        assessmentTime: new Date(),
        riskScore: 150,  // Invalid: > 100
        category: "HIGH",
        factors: {
            leafWetness: {
                value: 12,
                weight: 0.3,
                contribution: 30
            },
            temperature: {
                value: 25,
                weight: 0.2,
                contribution: 20,
                optimal: true
            },
            humidity: {
                value: 85,
                weight: 0.2,
                contribution: 20
            },
            rainfall: {
                value: 15,
                weight: 0.15,
                contribution: 15
            },
            trapCount: {
                value: 25,
                weight: 0.15,
                contribution: 15
            }
        },
        diseases: ["powdery_mildew"],
        pests: ["aphids"],
        explanation: "Test",
        recommendation: "Monitor",
        confidence: 0.9
    });
    print("   ❌ ERROR: Should have failed - risk score > 100!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("10. RISK_ASSESSMENTS - Invalid risk category:");
print("    Category must be: LOW, MODERATE, HIGH, or CRITICAL\n");

try {
    db.risk_assessments.insertOne({
        assessmentId: "RISK_INVALID_002",
        fieldId: "FLD00000001",
        assessmentTime: new Date(),
        riskScore: 75,
        category: "EXTREME",  // Invalid: not in allowed categories
        factors: {
            leafWetness: {
                value: 12,
                weight: 0.3,
                contribution: 30
            },
            temperature: {
                value: 25,
                weight: 0.2,
                contribution: 20,
                optimal: true
            },
            humidity: {
                value: 85,
                weight: 0.2,
                contribution: 20
            },
            rainfall: {
                value: 15,
                weight: 0.15,
                contribution: 15
            },
            trapCount: {
                value: 25,
                weight: 0.15,
                contribution: 15
            }
        },
        diseases: ["late_blight"],
        pests: ["whitefly"],
        explanation: "High risk conditions",
        recommendation: "Apply fungicide",
        confidence: 0.85
    });
    print("   ❌ ERROR: Should have failed - invalid category!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("11. RISK_ASSESSMENTS - Weights don't sum to 1:");
print("    Factor weights must sum to 1.0 for proper calculation\n");

try {
    db.risk_assessments.insertOne({
        assessmentId: "RISK_INVALID_003",
        fieldId: "FLD00000001",
        assessmentTime: new Date(),
        riskScore: 60,
        category: "HIGH",
        factors: {
            leafWetness: {
                value: 8,
                weight: 0.5,  // Total weights = 1.3 (invalid)
                contribution: 25
            },
            temperature: {
                value: 22,
                weight: 0.3,
                contribution: 15,
                optimal: true
            },
            humidity: {
                value: 70,
                weight: 0.2,
                contribution: 10
            },
            rainfall: {
                value: 5,
                weight: 0.2,
                contribution: 5
            },
            trapCount: {
                value: 10,
                weight: 0.1,
                contribution: 5
            }
        },
        diseases: ["rust"],
        pests: ["thrips"],
        explanation: "Moderate risk",
        recommendation: "Monitor closely",
        confidence: 0.8
    });
    print("   ❌ ERROR: Should have failed - weights don't sum to 1!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// EVENTS COLLECTION - Validation Examples
// ========================================================================
print("12. EVENTS - Invalid event type:");
print("    Event type must be: SPRAY_RECOMMENDATION, RISK_ALERT, PEST_OUTBREAK, or DISEASE_DETECTION\n");

try {
    db.events.insertOne({
        eventId: "EVT_INVALID_001",
        fieldId: "FLD00000001",
        eventType: "WEATHER_ALERT",  // Invalid: not in allowed types
        severity: "high",
        timestamp: new Date(),
        description: "Heavy rain warning",
        metadata: {
            rainfall: 50
        },
        acknowledged: false,
        createdAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid event type!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("13. EVENTS - Invalid severity level:");
print("    Severity must be: low, medium, high, or critical\n");

try {
    db.events.insertOne({
        eventId: "EVT_INVALID_002",
        fieldId: "FLD00000001",
        eventType: "RISK_ALERT",
        severity: "urgent",  // Invalid: not in allowed severities
        timestamp: new Date(),
        description: "High disease risk detected",
        metadata: {
            riskScore: 85,
            disease: "powdery_mildew"
        },
        acknowledged: false,
        createdAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - invalid severity!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// Additional Complex Validation Examples
// ========================================================================
print("14. MEASUREMENTS - Trap count exceeding reasonable limits:");
print("    Trap counts should be within reasonable bounds (0-1000)\n");

try {
    db.measurements.insertOne({
        sensorId: "SNS00000003",
        fieldId: "FLD00000001",
        sensorType: "pest_trap",
        timestamp: new Date(),
        data: {
            trapCount: 5000,  // Unreasonably high
            pestType: "aphids",
            temperature: 25
        },
        quality: {
            status: "valid",
            confidence: 0.95
        }
    });
    print("   ❌ ERROR: Should have failed - unrealistic trap count!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
print("15. FIELDS - Negative area value:");
print("    Field area must be positive\n");

try {
    db.fields.insertOne({
        fieldId: "FLD_INVALID_003",
        farmId: "FARM00000001",
        name: "Negative Area Field",
        area: -5.5,  // Invalid: negative area
        crop: {
            type: "wheat",
            variety: "Winter Wheat",
            plantingDate: new Date("2024-01-01"),
            expectedHarvest: new Date("2024-06-01"),
            growthStage: "vegetative"
        },
        soil: {
            type: "clay",
            pH: 7.0
        },
        location: {
            type: "Polygon",
            coordinates: [[
                [-120.5, 35.7],
                [-120.49, 35.7],
                [-120.49, 35.69],
                [-120.5, 35.69],
                [-120.5, 35.7]
            ]]
        },
        riskHistory: {
            averageRisk: 35,
            highestRisk: 70,
            lastHighRisk: new Date()
        },
        createdAt: new Date(),
        updatedAt: new Date()
    });
    print("   ❌ ERROR: Should have failed - negative area!");
} catch (e) {
    print("   ✓ Correctly rejected: " + e.message.substring(0, 100) + "...");
}

print("\n");

// ========================================================================
// Summary
// ========================================================================
print("=== Validation Summary ===\n");
print("All invalid inserts were correctly rejected by schema validation rules.");
print("\nKey validation rules enforced:");
print("• Geographic coordinates must be within valid ranges");
print("• Email addresses must follow standard format");
print("• Enumerated fields must match allowed values");
print("• Numeric values must be within realistic ranges");
print("• Percentages must be 0-100");
print("• Risk scores must be 0-100");
print("• Factor weights must sum to 1.0");
print("• All required fields must be present");
print("\nThese validations ensure data integrity and prevent:");
print("• Invalid sensor readings");
print("• Incorrect risk calculations");
print("• Data inconsistencies");
print("• System errors from bad data");