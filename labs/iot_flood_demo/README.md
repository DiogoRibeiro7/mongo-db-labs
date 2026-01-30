# IoT Flood Demo (MongoDB)

Teaching bundle for a flood-risk IoT project:
- Rivers + stormwater network + rain gauges
- Time series measurements
- Adaptive sampling (LOW/NORMAL/HIGH/CRITICAL)
- Alerts (OPEN/RESOLVED)

## Files

- `00_setup_mongodb.js` — creates collections, time-series config, and indexes
- `01_seed_flood_project.py` — seeds `sites`, `sensors`, `ratingCurves`, `samplingPolicies`, `policyState`
- `02_simulate_flood_project.py` — generates synthetic telemetry into `measurements`, updates `policyState`, emits `alerts`
- `03_queries_exam.js` — exam-style aggregation queries
- `DATABASE.md` — data dictionary (every key documented)
- `docker-compose.yml` — optional MongoDB container for labs
- `requirements.txt` — Python dependency for the seed/simulator scripts

## Quick start (local MongoDB)

1) Setup DB + indexes:
```bash
mongosh 00_setup_mongodb.js
```

2) Install Python dependency:
```bash
python -m pip install -r requirements.txt
```

3) Seed master/config data:
```bash
python 01_seed_flood_project.py
```

4) Generate time series:
```bash
python 02_simulate_flood_project.py --hours 6 --base-step-sec 10 --seed 7
```

5) Run the query sheet:
```bash
mongosh 03_queries_exam.js
```

## Quick start (Docker)

```bash
docker compose up -d
mongosh "mongodb://localhost:27017" 00_setup_mongodb.js
python -m pip install -r requirements.txt
python 01_seed_flood_project.py
python 02_simulate_flood_project.py --hours 6 --base-step-sec 10 --seed 7
mongosh "mongodb://localhost:27017" 03_queries_exam.js
```


## Schema Validation Exercises

This lab includes comprehensive schema validation to teach data integrity concepts.

### Files for Validation Teaching

1. **`00_setup_mongodb.js`** - Standard validation (production-ready)
2. **`00_setup_mongodb_strict.js`** - Enhanced validation (teaching-focused)
3. **`04_bad_inserts.js`** - Invalid document examples (20 test cases)

### Running Validation Tests

```bash
# Apply standard validation
mongosh 00_setup_mongodb.js

# Or apply stricter validation for teaching
mongosh 00_setup_mongodb_strict.js

# Test validation with invalid documents
mongosh 04_bad_inserts.js
```

### Key Validation Rules Demonstrated

| Collection | Validation Rules | Example Violations |
|------------|-----------------|-------------------|
| **sites** | • Site code format (uppercase alphanumeric)<br>• Coordinate ranges (-180 to 180, -90 to 90)<br>• Enum site types | Missing fields, invalid coordinates, wrong types |
| **sensors** | • Sensor code pattern (XX###)<br>• Valid metric enums<br>• Firmware version format | Invalid enum values, missing references |
| **measurements** | • Required timestamp<br>• Value ranges (-100 to 1000)<br>• Battery 0-100% | Negative water levels, out-of-range values |
| **alerts** | • Alert ID format (ALT+timestamp)<br>• Severity levels<br>• Message length (10-500) | Invalid severity, missing messages |
| **samplingPolicies** | • Interval ranges per mode<br>• Hysteresis 0.01-5.0m<br>• Battery constraints | Negative intervals, invalid modes |

### Exercises for Students

1. **Test Schema Enforcement**
   ```javascript
   // Try inserting a site with latitude > 90
   db.sites.insertOne({
     siteCode: "TEST001",
     location: { lat: 100, lon: 0 }  // Invalid!
   });
   ```

2. **Explore Validation Errors**
   ```bash
   # Run the bad inserts script
   mongosh 04_bad_inserts.js

   # Observe error messages and understand why each failed
   ```

3. **Modify Validation Rules**
   ```javascript
   // Temporarily relax validation
   db.runCommand({
     collMod: "measurements",
     validationLevel: "moderate"  // Allow existing invalid docs
   });
   ```

4. **Create Custom Validators**
   ```javascript
   // Add business rule: water level must be less than severe threshold
   validator: {
     $expr: {
       $lt: ["$waterLevelM", "$site.thresholds.severeLevelM"]
     }
   }
   ```

### Schema Validation Levels

- **`validationLevel`**:
  - `"strict"` - Validate all inserts and updates (default)
  - `"moderate"` - Only validate new documents
  - `"off"` - No validation

- **`validationAction`**:
  - `"error"` - Reject invalid documents (default)
  - `"warn"` - Log warnings but allow

### Disabling Validation (for testing)

```bash
# Disable validation temporarily
mongosh --eval 'db.getSiblingDB("iot_flood_demo").runCommand({collMod:"measurements",validationLevel:"off"})'

# Re-enable strict validation
mongosh --eval 'db.getSiblingDB("iot_flood_demo").runCommand({collMod:"measurements",validationLevel:"strict"})'
```
