// 00_setup_mongodb_strict.js
// Enhanced version with stricter schema validation
// Database: iot_flood_demo
// Purpose: Demonstrates comprehensive schema validation with tighter constraints
// Usage:
//   mongosh 00_setup_mongodb_strict.js

const dbName = "iot_flood_demo";
const dbRef = db.getSiblingDB(dbName);

print('\n' + '='.repeat(60));
print('APPLYING ENHANCED SCHEMA VALIDATION');
print('Tighter constraints for teaching validation concepts');
print('='.repeat(60) + '\n');

// Helper: apply a validator to an existing collection
function applyValidator(collectionName, validator) {
  const res = dbRef.runCommand({
    collMod: collectionName,
    validator: { $jsonSchema: validator },
    validationLevel: "strict",
    validationAction: "error"
  });

  if (!res.ok) {
    print(`❌ Failed to apply validator to ${collectionName}`);
    printjson(res);
  } else {
    print(`✅ Enhanced validator applied to ${collectionName}`);
  }
}

// Strict enums with limited options
const SITE_TYPES = ["river", "stormwater", "rain_gauge"];
const POWER_TYPES = ["battery", "mains", "solar"];
const SENSOR_STATUS = ["active", "inactive", "maintenance"];
const MODES = ["LOW", "NORMAL", "HIGH", "CRITICAL"];
const ALERT_STATUS = ["OPEN", "ACKNOWLEDGED", "RESOLVED"];
const ALERT_SEVERITY = ["info", "warning", "critical"];
const METRICS = ["waterLevelM", "flowRateM3s", "rainfallRateMmh", "batteryV", "temperatureC"];
const ALERT_TYPES = ["high_water", "rapid_rise", "sensor_offline", "battery_low", "data_quality"];

// --- ENHANCED sites schema ---
applyValidator("sites", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteCode", "siteType", "name", "catchmentId", "geo", "thresholds", "createdAt"],
  properties: {
    _id: { bsonType: "objectId" },
    siteCode: {
      bsonType: "string",
      pattern: "^[A-Z][A-Z0-9]{3,9}$",  // Uppercase alphanumeric, 4-10 chars
      description: "Site code must be uppercase alphanumeric, 4-10 characters"
    },
    siteType: {
      enum: SITE_TYPES,
      description: "Must be one of: river, stormwater, rain_gauge"
    },
    name: {
      bsonType: "string",
      minLength: 3,
      maxLength: 100,
      pattern: "^[A-Za-z0-9\\s\\-\\.]+$",  // Alphanumeric with spaces, hyphens, dots
      description: "Site name with standard characters only"
    },
    catchmentId: {
      bsonType: "string",
      pattern: "^CAT[0-9]{3,6}$",  // Format: CAT### to CAT######
      description: "Catchment ID must follow format CAT###"
    },
    geo: {
      bsonType: "object",
      additionalProperties: false,
      required: ["type", "coordinates"],
      properties: {
        type: {
          enum: ["Point"],
          description: "GeoJSON type must be Point"
        },
        coordinates: {
          bsonType: "array",
          minItems: 2,
          maxItems: 2,
          items: [
            { bsonType: "double", minimum: -180, maximum: 180 },  // longitude
            { bsonType: "double", minimum: -90, maximum: 90 }      // latitude
          ],
          description: "Coordinates as [longitude, latitude]"
        }
      }
    },
    thresholds: {
      bsonType: "object",
      additionalProperties: false,
      required: ["watchLevelM", "warningLevelM", "severeLevelM"],
      properties: {
        watchLevelM: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 100.0,
          description: "Watch level in meters (0-100)"
        },
        warningLevelM: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 100.0,
          description: "Warning level in meters (0-100)"
        },
        severeLevelM: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 100.0,
          description: "Severe level in meters (0-100)"
        },
        surchargeLevelM: {
          bsonType: ["double", "null"],
          minimum: 0.0,
          maximum: 100.0,
          description: "Optional surcharge level"
        },
        overflowLevelM: {
          bsonType: ["double", "null"],
          minimum: 0.0,
          maximum: 100.0,
          description: "Optional overflow level"
        }
      }
    },
    createdAt: { bsonType: "date" },
    updatedAt: { bsonType: ["date", "null"] },
    description: {
      bsonType: ["string", "null"],
      maxLength: 500,
      description: "Optional site description"
    }
  }
});

// --- ENHANCED sensors schema ---
applyValidator("sensors", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteId", "sensorCode", "metric", "unit", "hardware", "powerType", "installedAt", "status"],
  properties: {
    _id: { bsonType: "objectId" },
    siteId: { bsonType: "objectId" },
    sensorCode: {
      bsonType: "string",
      pattern: "^[A-Z]{2}[0-9]{3,6}$",  // Format: XX### to XX######
      description: "Sensor code format: 2 uppercase letters + 3-6 digits"
    },
    metric: {
      enum: METRICS,
      description: "Measurement type from allowed metrics"
    },
    unit: {
      bsonType: "string",
      enum: ["m", "m³/s", "mm/h", "V", "°C", "%"],
      description: "Standard unit of measurement"
    },
    hardware: {
      bsonType: "object",
      additionalProperties: false,
      required: ["model", "vendor", "firmwareVersion"],
      properties: {
        model: {
          bsonType: "string",
          minLength: 2,
          maxLength: 50,
          pattern: "^[A-Za-z0-9\\-\\.]+$"
        },
        vendor: {
          bsonType: "string",
          enum: ["Campbell", "HOBO", "YSI", "Vaisala", "Stevens", "Other"],
          description: "Sensor manufacturer"
        },
        firmwareVersion: {
          bsonType: "string",
          pattern: "^[0-9]+\\.[0-9]+\\.[0-9]+$",  // Semantic versioning
          description: "Firmware version (e.g., 1.2.3)"
        }
      }
    },
    powerType: { enum: POWER_TYPES },
    installedAt: { bsonType: "date" },
    lastMaintenanceAt: { bsonType: ["date", "null"] },
    status: { enum: SENSOR_STATUS },
    calibration: {
      bsonType: ["object", "null"],
      additionalProperties: false,
      properties: {
        offset: { bsonType: "double", minimum: -10, maximum: 10 },
        scale: { bsonType: "double", minimum: 0.5, maximum: 2.0 },
        lastCalibratedAt: { bsonType: "date" }
      }
    }
  }
});

// --- ENHANCED measurements schema (time-series) ---
applyValidator("measurements", {
  bsonType: "object",
  additionalProperties: false,
  required: ["ts", "meta", "value"],
  properties: {
    _id: { bsonType: "objectId" },
    ts: { bsonType: "date" },
    meta: {
      bsonType: "object",
      additionalProperties: false,
      required: ["siteId", "sensorId", "metric"],
      properties: {
        siteId: { bsonType: "objectId" },
        sensorId: { bsonType: "objectId" },
        metric: { enum: METRICS }
      }
    },
    value: {
      bsonType: "double",
      minimum: -100,  // Allow negative for temperature
      maximum: 1000,  // Reasonable upper limit
      description: "Measurement value with reasonable bounds"
    },
    batteryPct: {
      bsonType: ["int", "null"],
      minimum: 0,
      maximum: 100,
      description: "Battery percentage (0-100)"
    },
    signalQuality: {
      bsonType: ["double", "null"],
      minimum: 0.0,
      maximum: 1.0,
      description: "Signal quality (0.0-1.0)"
    },
    qcFlags: {
      bsonType: ["array", "null"],
      maxItems: 10,
      items: {
        bsonType: "string",
        enum: ["MISSING", "SPIKE", "FLATLINE", "OUT_OF_RANGE", "MANUAL_OVERRIDE"],
        description: "Quality control flags"
      }
    }
  }
});

// --- ENHANCED alerts schema ---
applyValidator("alerts", {
  bsonType: "object",
  additionalProperties: false,
  required: ["alertId", "ts", "siteId", "alertType", "status", "severity", "message", "createdAt"],
  properties: {
    _id: { bsonType: "objectId" },
    alertId: {
      bsonType: "string",
      pattern: "^ALT[0-9]{10,}$",  // Format: ALT + timestamp
      description: "Alert ID format: ALT + timestamp"
    },
    ts: { bsonType: "date" },
    siteId: { bsonType: "objectId" },
    sensorId: { bsonType: ["objectId", "null"] },
    alertType: {
      enum: ALERT_TYPES,
      description: "Type of alert from predefined list"
    },
    status: { enum: ALERT_STATUS },
    severity: { enum: ALERT_SEVERITY },
    message: {
      bsonType: "string",
      minLength: 10,
      maxLength: 500,
      description: "Alert message (10-500 chars)"
    },
    thresholdValue: {
      bsonType: ["double", "null"],
      minimum: 0,
      maximum: 1000,
      description: "Threshold that triggered alert"
    },
    measuredValue: {
      bsonType: ["double", "null"],
      minimum: -100,
      maximum: 1000,
      description: "Actual measured value"
    },
    context: {
      bsonType: ["object", "null"],
      additionalProperties: false,
      properties: {
        trend: { enum: ["rising", "falling", "stable", null] },
        duration: { bsonType: ["int", "null"], minimum: 0 },
        previousValue: { bsonType: ["double", "null"] }
      }
    },
    acknowledgedBy: {
      bsonType: ["string", "null"],
      pattern: "^[a-zA-Z0-9_]+$",
      description: "Username who acknowledged"
    },
    acknowledgedAt: { bsonType: ["date", "null"] },
    resolvedAt: { bsonType: ["date", "null"] },
    createdAt: { bsonType: "date" }
  }
});

// --- ENHANCED samplingPolicies schema ---
applyValidator("samplingPolicies", {
  bsonType: "object",
  additionalProperties: false,
  required: ["policyId", "siteId", "enabled", "modes", "hysteresisMarginM", "cooldownSec", "updatedAt"],
  properties: {
    _id: { bsonType: "objectId" },
    policyId: {
      bsonType: "string",
      pattern: "^POL[0-9]{6}$",  // Format: POL######
      description: "Policy ID format: POL + 6 digits"
    },
    siteId: { bsonType: "objectId" },
    enabled: { bsonType: "bool" },
    modes: {
      bsonType: "object",
      additionalProperties: false,
      required: ["LOW", "NORMAL", "HIGH", "CRITICAL"],
      properties: {
        LOW: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: {
              bsonType: "int",
              minimum: 300,    // Min 5 minutes
              maximum: 86400,  // Max 24 hours
              description: "Sampling interval (300-86400 seconds)"
            },
            minDurationSec: {
              bsonType: "int",
              minimum: 0,
              maximum: 3600,
              description: "Minimum duration (0-3600 seconds)"
            }
          }
        },
        NORMAL: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 60, maximum: 3600 },
            minDurationSec: { bsonType: "int", minimum: 0, maximum: 1800 }
          }
        },
        HIGH: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 30, maximum: 600 },
            minDurationSec: { bsonType: "int", minimum: 0, maximum: 900 }
          }
        },
        CRITICAL: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 10, maximum: 300 },
            minDurationSec: { bsonType: "int", minimum: 0, maximum: 600 }
          }
        }
      }
    },
    hysteresisMarginM: {
      bsonType: "double",
      minimum: 0.01,
      maximum: 5.0,
      description: "Hysteresis margin in meters (0.01-5.0)"
    },
    cooldownSec: {
      bsonType: "int",
      minimum: 0,
      maximum: 3600,
      description: "Cooldown period (0-3600 seconds)"
    },
    batteryConstraints: {
      bsonType: ["object", "null"],
      additionalProperties: false,
      required: ["lowBatteryPct", "criticalBatteryPct"],
      properties: {
        lowBatteryPct: { bsonType: "int", minimum: 10, maximum: 50 },
        criticalBatteryPct: { bsonType: "int", minimum: 5, maximum: 30 }
      }
    },
    triggers: {
      bsonType: ["object", "null"],
      additionalProperties: false,
      properties: {
        rainfallHighMmh: { bsonType: "double", minimum: 0.0, maximum: 500.0 },
        riseRateHighMperMin: { bsonType: "double", minimum: 0.0, maximum: 1.0 },
        riseRateCriticalMperMin: { bsonType: "double", minimum: 0.0, maximum: 2.0 }
      }
    },
    updatedAt: { bsonType: "date" }
  }
});

print('\n✅ Enhanced schema validation applied to all collections');
print('Run 04_bad_inserts.js to test validation rules\n');