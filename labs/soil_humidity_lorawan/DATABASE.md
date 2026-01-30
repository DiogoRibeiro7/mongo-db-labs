# Database Documentation — `iot_flood_demo` (MongoDB)

This document describes the MongoDB database used for the IoT flood monitoring project.
It includes all collections, their purpose, relationships, and a data dictionary where every key has a description.

## Scope

The database supports:

- River monitoring (water level, velocity, derived flow rate)
- Stormwater network monitoring (water level, velocity, derived flow rate)
- Rain gauges (rain rate and cumulative rainfall)
- Adaptive sampling (dynamic measurement frequency based on risk and battery constraints)
- Alerts (OPEN/RESOLVED events with context)

## Collections

- `sites`
- `sensors`
- `measurements` (time series)
- `ratingCurves`
- `samplingPolicies`
- `policyState`
- `alerts`

## Core Relationships

- `sites._id` is referenced by:
  - `sensors.siteId`
  - `ratingCurves.siteId`
  - `samplingPolicies.siteId`
  - `policyState.siteId`
  - `alerts.siteId`
  - `measurements.meta.siteId`
- `sensors._id` is referenced by:
  - `measurements.meta.sensorId`

## Naming and Units

- `ts` fields are UTC `Date`.
- Metrics are camelCase and include units in the field name when helpful:
  - `waterLevelM` (m)
  - `flowVelocityMps` (m/s)
  - `flowRateM3s` (m³/s)
  - `rainfallRateMmh` (mm/h)
  - `rainfallAccumMm` (mm)

---

# 1) Collection: `sites`

## Purpose
Master list of monitored locations:
- river stations (`siteType="river"`)
- stormwater nodes (`siteType="stormwater"`)
- rain gauges (`siteType="rain_gauge"`)

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for the site document. |
| `siteCode` | string | Yes | Human-readable unique code (e.g., `RIVER_001`, `SW_001`, `RG_001`). |
| `siteType` | string | Yes | Type of site: `river`, `stormwater`, or `rain_gauge`. |
| `name` | string | Yes | Display name for dashboards and reports. |
| `catchmentId` | string | Yes | Catchment/basin identifier (links rain gauges to downstream sites). |
| `geo` | object | Yes | GeoJSON location object. |
| `geo.type` | string | Yes | GeoJSON type; must be `Point`. |
| `geo.coordinates` | array[number, number] | Yes | `[longitude, latitude]` in WGS84. |
| `thresholds` | object | Yes | Operational thresholds for alerts and policy escalation. |
| `thresholds.watchLevelM` | number \| null | Yes | River: WATCH threshold (m). Null for other site types. |
| `thresholds.warningLevelM` | number \| null | Yes | River: WARNING threshold (m). Null for other site types. |
| `thresholds.severeLevelM` | number \| null | Yes | River: SEVERE threshold (m). Null for other site types. |
| `thresholds.surchargeLevelM` | number \| null | Yes | Stormwater: SURCHARGE threshold (m). Null for other site types. |
| `thresholds.overflowLevelM` | number \| null | Yes | Stormwater: OVERFLOW threshold (m). Null for other site types. |
| `createdAt` | Date | Yes | Document creation time (UTC). |

## Indexes
- Unique: `{ siteCode: 1 }`
- Supporting: `{ catchmentId: 1, siteType: 1 }`

---

# 2) Collection: `sensors`

## Purpose
Defines sensor channels installed at each site. Each sensor emits one metric (or represents a derived metric channel).

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for the sensor channel. |
| `siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `sensorCode` | string | Yes | Human-readable unique sensor code (e.g., `WATERLEVELM_RIVER_001`). |
| `metric` | string | Yes | Metric name produced by this sensor channel. |
| `unit` | string | Yes | Unit of the metric (e.g., `m`, `m/s`, `mm/h`, `m3/s`). |
| `hardware` | object | Yes | Hardware metadata. |
| `hardware.model` | string | Yes | Sensor model name. |
| `hardware.vendor` | string | Yes | Sensor vendor/manufacturer. |
| `powerType` | string | Yes | Power source: `battery`, `mains`, or `solar`. |
| `installedAt` | Date | Yes | Installation timestamp (UTC). |
| `status` | string | Yes | Operational status: `active` or `inactive`. |

## Allowed `metric` values (project default)
- `waterLevelM`
- `flowVelocityMps`
- `flowRateM3s`
- `rainfallRateMmh`
- `rainfallAccumMm`

## Indexes
- Unique: `{ sensorCode: 1 }`
- Supporting: `{ siteId: 1, metric: 1 }`

---

# 3) Collection: `measurements` (Time Series)

## Purpose
Stores all time series telemetry in a single collection. One document represents one metric value at a given time.

## Time series configuration (MongoDB)
- `timeField`: `ts`
- `metaField`: `meta`
- `granularity`: `seconds`

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `ts` | Date | Yes | Measurement timestamp (UTC). |
| `meta` | object | Yes | Metadata partitioning for time series. |
| `meta.siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `meta.sensorId` | ObjectId | Yes | Reference to `sensors._id`. |
| `meta.metric` | string | Yes | Metric name (must match `sensors.metric`). |
| `value` | number | Yes | Measured value for `meta.metric`. |
| `batteryPct` | int | No | Battery level percent (0–100). |
| `signalQuality` | number | No | Normalized signal quality (0–1). |
| `qcFlags` | array[string] | No | Data quality flags describing validation results. |

## Recommended `qcFlags`
- `OK`
- `RANGE_VIOLATION`
- `SPIKE_SUSPECTED`
- `STUCK_SENSOR`
- `MISSING_VALUE`
- `EXTRAPOLATED`

## Indexes
- Supporting: `{ "meta.siteId": 1, ts: 1 }`

---

# 4) Collection: `ratingCurves`

## Purpose
Calibration mapping from water level to flow rate for river (and optionally stormwater) sites.

## Curve types
- `powerLaw`: `Q = a * max(0, h - h0)^b`
- `tableLookup`: discrete table mapping
- `empirical`: simplified fitted form

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for a curve version. |
| `siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `curveType` | string | Yes | `powerLaw`, `tableLookup`, or `empirical`. |
| `version` | int | Yes | Curve version number. |
| `validFrom` | Date | Yes | When this curve becomes valid. |
| `validTo` | Date \| null | Yes | When this curve expires; null means active. |
| `params` | object | Yes | Parameters for the chosen curve type. |
| `params.a` | number | Depends | Power-law coefficient (required for `powerLaw`). |
| `params.h0` | number | Depends | Power-law offset (required for `powerLaw`). |
| `params.b` | number | Depends | Power-law exponent (required for `powerLaw`). |
| `range` | object | Yes | Calibration validity range. |
| `range.minLevelM` | number | Yes | Minimum calibrated level (m). |
| `range.maxLevelM` | number | Yes | Maximum calibrated level (m). |
| `updatedAt` | Date | Yes | Last update timestamp. |

## Indexes
- Supporting: `{ siteId: 1, version: -1 }`

---

# 5) Collection: `samplingPolicies`

## Purpose
Adaptive sampling configuration per site. Used to decide measurement frequency based on risk and battery constraints.

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for the sampling policy. |
| `siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `enabled` | bool | Yes | If false, auto mode changes are disabled. |
| `modes` | object | Yes | Sampling modes configuration. |
| `modes.LOW` | object | Yes | Low-frequency, energy saving mode. |
| `modes.LOW.intervalSec` | int | Yes | Sampling interval (seconds). |
| `modes.LOW.minDurationSec` | int | Yes | Minimum time to stay in this mode. |
| `modes.NORMAL` | object | Yes | Baseline mode. |
| `modes.NORMAL.intervalSec` | int | Yes | Sampling interval (seconds). |
| `modes.NORMAL.minDurationSec` | int | Yes | Minimum time to stay in this mode. |
| `modes.HIGH` | object | Yes | Higher frequency for elevated risk. |
| `modes.HIGH.intervalSec` | int | Yes | Sampling interval (seconds). |
| `modes.HIGH.minDurationSec` | int | Yes | Minimum time to stay in this mode. |
| `modes.CRITICAL` | object | Yes | Highest frequency for severe conditions. |
| `modes.CRITICAL.intervalSec` | int | Yes | Sampling interval (seconds). |
| `modes.CRITICAL.minDurationSec` | int | Yes | Minimum time to stay in this mode. |
| `hysteresisMarginM` | number | Yes | Level margin (m) to avoid oscillation around thresholds. |
| `cooldownSec` | int | Yes | Cooldown time between mode changes. |
| `batteryConstraints` | object | Yes | Battery constraints affecting escalation. |
| `batteryConstraints.lowBatteryPct` | int | Yes | Below this, policy avoids high modes if possible. |
| `batteryConstraints.forbidCriticalBelowPct` | int | Yes | Below this, CRITICAL is forbidden. |
| `triggers` | object | Yes | Additional escalation triggers. |
| `triggers.rainfallHighMmh` | number | Yes | Rain rate threshold for HIGH. |
| `triggers.rainfallMediumMmh` | number | Yes | Rain rate threshold for NORMAL. |
| `triggers.riseHighMperMin` | number | Yes | Rise rate threshold for HIGH. |
| `triggers.riseCriticalMperMin` | number | Yes | Rise rate threshold for CRITICAL. |
| `updatedAt` | Date | Yes | Last update timestamp. |

## Indexes
- Unique: `{ siteId: 1 }`

---

# 6) Collection: `policyState`

## Purpose
Current sampling mode per site and decision metadata.

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for the state document. |
| `siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `currentMode` | string | Yes | Current mode: `LOW`, `NORMAL`, `HIGH`, `CRITICAL`. |
| `lastChangeTs` | Date | Yes | Timestamp of last mode change. |
| `lastDecisionReason` | string | Yes | Reason for last decision (audit). |
| `cooldownUntilTs` | Date | Yes | Timestamp until which changes are blocked. |
| `batteryPctLast` | int | Yes | Battery percent used in last decision. |
| `updatedAt` | Date | Yes | Last update timestamp. |

## Indexes
- Unique: `{ siteId: 1 }`

---

# 7) Collection: `alerts`

## Purpose
Append-only alert event log. Each change is a new document.

## Schema (data dictionary)

| Key | Type | Required | Description |
|---|---:|:---:|---|
| `_id` | ObjectId | Yes | Unique identifier for this alert event. |
| `ts` | Date | Yes | Timestamp of the alert event (UTC). |
| `siteId` | ObjectId | Yes | Reference to `sites._id`. |
| `alertType` | string | Yes | Alert category (see values below). |
| `status` | string | Yes | `OPEN` or `RESOLVED`. |
| `severity` | string | Yes | Severity label (`info`, `medium`, `high`, `critical`). |
| `context` | object | Yes | Snapshot of relevant values at event time. |
| `context.waterLevelM` | number | No | Water level at event time (if applicable). |
| `context.dLevelDtMperMin` | number | No | Rise rate at event time (if available). |
| `context.rainfallRateMmh` | number | No | Rain rate at event time (if available). |
| `context.mode` | string | No | Sampling mode at event time. |
| `context.batteryPct` | int | No | Battery percent at event time. |
| `createdAt` | Date | Yes | Insert timestamp (UTC). |

## Allowed `alertType` values (project default)
- Rivers: `FLOOD_WATCH`, `FLOOD_WARNING`, `FLOOD_SEVERE`
- Stormwater: `STORMWATER_SURCHARGE`, `STORMWATER_OVERFLOW`
- Optional: `SENSOR_FAULT`, `DATA_GAP`, `EXTRAPOLATION_WARNING`

## Indexes
- Supporting: `{ siteId: 1, status: 1, ts: -1 }`

---

# Retention (teaching suggestion)

If you want to teach lifecycle policies:

- Keep `sites`, `sensors`, `ratingCurves`, `samplingPolicies` indefinitely.
- Keep `policyState` only latest per site.
- Keep `measurements` for N days (or export to cold storage).
- Keep `alerts` longer than measurements (for post-mortem analysis).

---

# Quick run order (lab)

1. Create collections and indexes:
   ```bash
   mongosh 00_setup_mongodb.js
   ```

2. Seed master/config data:
   ```bash
   python 01_seed_flood_project.py
   ```

3. Generate simulated telemetry + policy changes + alerts:
   ```bash
   python 02_simulate_flood_project.py --hours 6 --base-step-sec 10 --seed 7
   ```

4. Run exam queries:
   ```bash
   mongosh 03_queries_exam.js
   ```


---

# Schema validation notes

This project uses MongoDB collection validation (`$jsonSchema`) for teaching.

- Goal: students learn **constraints** (types, required keys, enums) and see what happens when they insert invalid data.
- Validators are defined in `00_setup_mongodb.js` via `collMod`.

## Disable validation (optional)

If you need to let students insert malformed documents for an exercise:

```js
db.runCommand({ collMod: "measurements", validationLevel: "off" })
```

You can re-enable it:

```js
db.runCommand({ collMod: "measurements", validationLevel: "strict" })
```
