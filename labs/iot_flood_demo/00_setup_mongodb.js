// 00_setup_mongodb.js
// Database: iot_flood_demo
// Usage:
//   mongosh 00_setup_mongodb.js
//
// This setup script creates collections, configures a time-series collection,
// creates indexes, and applies schema validation rules (using $jsonSchema).
//
// Notes:
// - Validation is set to: validationLevel="strict" and validationAction="error".
// - If you want to disable validation for a lab, you can run:
//     db.runCommand({ collMod: "<collection>", validationLevel: "off" })

const dbName = "iot_flood_demo";
const dbRef = db.getSiblingDB(dbName);

// ------------------------------------------------------------------
// Drop for clean, repeatable teaching runs (ignore errors if missing)
// ------------------------------------------------------------------
[
  "sites",
  "sensors",
  "ratingCurves",
  "samplingPolicies",
  "policyState",
  "alerts",
  "measurements"
].forEach((c) => {
  try { dbRef[c].drop(); } catch (e) {}
});

// ------------------------------------------------------------------
// Create collections
// ------------------------------------------------------------------
dbRef.createCollection("sites");
dbRef.createCollection("sensors");
dbRef.createCollection("ratingCurves");
dbRef.createCollection("samplingPolicies");
dbRef.createCollection("policyState");
dbRef.createCollection("alerts");

// Time-series for measurements
dbRef.createCollection("measurements", {
  timeseries: { timeField: "ts", metaField: "meta", granularity: "seconds" }
});

// ------------------------------------------------------------------
// Apply schema validation ($jsonSchema)
// ------------------------------------------------------------------

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
    print(`✅ Validator applied to ${collectionName}`);
  }
}

// Shared enums
const SITE_TYPES = ["river", "stormwater", "rain_gauge"];
const POWER_TYPES = ["battery", "mains", "solar"];
const SENSOR_STATUS = ["active", "inactive"];
const MODES = ["LOW", "NORMAL", "HIGH", "CRITICAL"];
const ALERT_STATUS = ["OPEN", "RESOLVED"];
const ALERT_SEVERITY = ["info", "medium", "high", "critical"];
const METRICS = ["waterLevelM", "flowVelocityMps", "flowRateM3s", "rainfallRateMmh", "rainfallAccumMm"];

// --- sites ---
applyValidator("sites", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteCode", "siteType", "name", "catchmentId", "geo", "thresholds", "createdAt"],
  properties: {
    _id: { bsonType: "objectId" },
    siteCode: { bsonType: "string", minLength: 3 },
    siteType: { enum: SITE_TYPES },
    name: { bsonType: "string", minLength: 3 },
    catchmentId: { bsonType: "string", minLength: 3 },
    geo: {
      bsonType: "object",
      additionalProperties: false,
      required: ["type", "coordinates"],
      properties: {
        type: { enum: ["Point"] },
        coordinates: {
          bsonType: "array",
          minItems: 2,
          maxItems: 2,
          items: [{ bsonType: "double" }, { bsonType: "double" }]
        }
      }
    },
    thresholds: {
      bsonType: "object",
      additionalProperties: false,
      required: ["watchLevelM", "warningLevelM", "severeLevelM", "surchargeLevelM", "overflowLevelM"],
      properties: {
        watchLevelM: { bsonType: ["double", "null"] },
        warningLevelM: { bsonType: ["double", "null"] },
        severeLevelM: { bsonType: ["double", "null"] },
        surchargeLevelM: { bsonType: ["double", "null"] },
        overflowLevelM: { bsonType: ["double", "null"] }
      }
    },
    createdAt: { bsonType: "date" }
  }
});

// --- sensors ---
applyValidator("sensors", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteId", "sensorCode", "metric", "unit", "hardware", "powerType", "installedAt", "status"],
  properties: {
    _id: { bsonType: "objectId" },
    siteId: { bsonType: "objectId" },
    sensorCode: { bsonType: "string", minLength: 3 },
    metric: { enum: METRICS },
    unit: { bsonType: "string", minLength: 1 },
    hardware: {
      bsonType: "object",
      additionalProperties: false,
      required: ["model", "vendor"],
      properties: {
        model: { bsonType: "string", minLength: 1 },
        vendor: { bsonType: "string", minLength: 1 }
      }
    },
    powerType: { enum: POWER_TYPES },
    installedAt: { bsonType: "date" },
    status: { enum: SENSOR_STATUS }
  }
});

// --- ratingCurves ---
applyValidator("ratingCurves", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteId", "curveType", "version", "validFrom", "validTo", "params", "range", "updatedAt"],
  properties: {
    _id: { bsonType: "objectId" },
    siteId: { bsonType: "objectId" },
    curveType: { enum: ["powerLaw", "tableLookup", "empirical"] },
    version: { bsonType: "int", minimum: 1 },
    validFrom: { bsonType: "date" },
    validTo: { bsonType: ["date", "null"] },
    params: {
      bsonType: "object",
      additionalProperties: true,
      properties: {
        a: { bsonType: "double" },
        h0: { bsonType: "double" },
        b: { bsonType: "double" }
      }
    },
    range: {
      bsonType: "object",
      additionalProperties: false,
      required: ["minLevelM", "maxLevelM"],
      properties: {
        minLevelM: { bsonType: "double" },
        maxLevelM: { bsonType: "double" }
      }
    },
    updatedAt: { bsonType: "date" }
  }
});

// --- samplingPolicies ---
applyValidator("samplingPolicies", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteId", "enabled", "modes", "hysteresisMarginM", "cooldownSec", "batteryConstraints", "triggers", "updatedAt"],
  properties: {
    _id: { bsonType: "objectId" },
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
            intervalSec: { bsonType: "int", minimum: 1 },
            minDurationSec: { bsonType: "int", minimum: 0 }
          }
        },
        NORMAL: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 1 },
            minDurationSec: { bsonType: "int", minimum: 0 }
          }
        },
        HIGH: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 1 },
            minDurationSec: { bsonType: "int", minimum: 0 }
          }
        },
        CRITICAL: {
          bsonType: "object",
          additionalProperties: false,
          required: ["intervalSec", "minDurationSec"],
          properties: {
            intervalSec: { bsonType: "int", minimum: 1 },
            minDurationSec: { bsonType: "int", minimum: 0 }
          }
        }
      }
    },
    hysteresisMarginM: { bsonType: "double", minimum: 0.0 },
    cooldownSec: { bsonType: "int", minimum: 0 },
    batteryConstraints: {
      bsonType: "object",
      additionalProperties: false,
      required: ["lowBatteryPct", "forbidCriticalBelowPct"],
      properties: {
        lowBatteryPct: { bsonType: "int", minimum: 0, maximum: 100 },
        forbidCriticalBelowPct: { bsonType: "int", minimum: 0, maximum: 100 }
      }
    },
    triggers: {
      bsonType: "object",
      additionalProperties: false,
      required: ["rainfallHighMmh", "rainfallMediumMmh", "riseHighMperMin", "riseCriticalMperMin"],
      properties: {
        rainfallHighMmh: { bsonType: "double", minimum: 0.0 },
        rainfallMediumMmh: { bsonType: "double", minimum: 0.0 },
        riseHighMperMin: { bsonType: "double", minimum: 0.0 },
        riseCriticalMperMin: { bsonType: "double", minimum: 0.0 }
      }
    },
    updatedAt: { bsonType: "date" }
  }
});

// --- policyState ---
applyValidator("policyState", {
  bsonType: "object",
  additionalProperties: false,
  required: ["siteId", "currentMode", "lastChangeTs", "lastDecisionReason", "cooldownUntilTs", "batteryPctLast", "updatedAt"],
  properties: {
    _id: { bsonType: "objectId" },
    siteId: { bsonType: "objectId" },
    currentMode: { enum: MODES },
    lastChangeTs: { bsonType: "date" },
    lastDecisionReason: { bsonType: "string" },
    cooldownUntilTs: { bsonType: "date" },
    batteryPctLast: { bsonType: "int", minimum: 0, maximum: 100 },
    updatedAt: { bsonType: "date" }
  }
});

// --- alerts ---
applyValidator("alerts", {
  bsonType: "object",
  additionalProperties: false,
  required: ["ts", "siteId", "alertType", "status", "severity", "context", "createdAt"],
  properties: {
    _id: { bsonType: "objectId" },
    ts: { bsonType: "date" },
    siteId: { bsonType: "objectId" },
    alertType: {
      bsonType: "string",
      minLength: 3
      // (kept flexible so you can teach "schema evolution" by adding new alert types)
    },
    status: { enum: ALERT_STATUS },
    severity: { enum: ALERT_SEVERITY },
    context: { bsonType: "object" }, // flexible snapshot
    createdAt: { bsonType: "date" }
  }
});

// --- measurements (time series) ---
// Note: validators work on time-series collections too.
// Keep it reasonably strict while allowing optional fields.
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
    value: { bsonType: "double" },
    batteryPct: { bsonType: ["int", "null"], minimum: 0, maximum: 100 },
    signalQuality: { bsonType: ["double", "null"], minimum: 0.0, maximum: 1.0 },
    qcFlags: {
      bsonType: ["array", "null"],
      items: { bsonType: "string" }
    }
  }
});

// ------------------------------------------------------------------
// Indexes
// ------------------------------------------------------------------
dbRef.sites.createIndex({ siteCode: 1 }, { unique: true });
dbRef.sites.createIndex({ catchmentId: 1, siteType: 1 });

dbRef.sensors.createIndex({ sensorCode: 1 }, { unique: true });
dbRef.sensors.createIndex({ siteId: 1, metric: 1 });

dbRef.ratingCurves.createIndex({ siteId: 1, version: -1 });

dbRef.samplingPolicies.createIndex({ siteId: 1 }, { unique: true });
dbRef.policyState.createIndex({ siteId: 1 }, { unique: true });

dbRef.alerts.createIndex({ siteId: 1, status: 1, ts: -1 });
dbRef.measurements.createIndex({ "meta.siteId": 1, ts: 1 });

print(`\n✅ Setup complete for database: ${dbName} (with schema validation)\n`);
