# Soil Humidity LoRaWAN Monitoring Lab

Agricultural soil monitoring system using LoRaWAN sensors for precision farming and irrigation management.

## Learning Objectives

- Design time-series collections for IoT sensor data
- Implement agricultural domain models with MongoDB
- Use geospatial indexes for farm field boundaries
- Create adaptive irrigation strategies based on soil moisture
- Analyze sensor data patterns with aggregation pipelines
- Handle LoRaWAN-specific IoT patterns

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series features)
- Python 3.10+
- Basic understanding of IoT concepts and agriculture

## Quick Start

### Local MongoDB

```bash
# 1. Setup database and collections
mongosh 00_setup_mongodb.js

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Seed master data (farms, fields, sensors, crops)
python 01_seed_soil_humidity.py

# 4. Simulate sensor readings (24 hours of data)
python 02_simulate_soil_humidity.py --hours 24

# 5. Run query exercises
mongosh 03_queries_exam.js
```

### Using Docker

```bash
# Start MongoDB container
docker compose up -d

# Run setup and seeding
mongosh mongodb://localhost:27017 00_setup_mongodb.js
python 01_seed_soil_humidity.py
python 02_simulate_soil_humidity.py --hours 24
mongosh mongodb://localhost:27017 03_queries_exam.js

# Stop when done
docker compose down
```

## Database Schema

This lab uses the `soil_humidity_lorawan` database with 7 collections:

- **farms** - Agricultural sites with owner information
- **fields** - Individual crop fields within farms
- **sensors** - LoRaWAN soil monitoring devices
- **measurements** - Time-series sensor readings (moisture, temperature, pH)
- **irrigationEvents** - Scheduled and completed irrigation activities
- **alerts** - Notifications for critical soil conditions
- **cropTypes** - Reference data for different crops

See [DATABASE.md](DATABASE.md) for complete schema documentation.

## Key Features Demonstrated

### 1. Time-Series Data
- Soil moisture measurements at different depths
- Temperature variations throughout the day
- Efficient storage with MongoDB time-series collections

### 2. Geospatial Queries
- Farm and field locations using GeoJSON
- Finding sensors within field boundaries
- Distance calculations for irrigation planning

### 3. Agricultural Analytics
- Soil moisture trends by field and depth
- Irrigation effectiveness analysis
- Crop-specific moisture requirements
- Alert generation for critical conditions

### 4. LoRaWAN IoT Patterns
- Device EUI management
- Battery monitoring
- Signal quality tracking
- Adaptive sampling based on conditions

## Schema Validation Exercises

This lab includes comprehensive schema validation for agricultural IoT data integrity.

### Validation Files

1. **`00_setup_mongodb.js`** - Standard collection setup with validation
2. **`04_bad_inserts.js`** - Test validation with 23 invalid document examples

### Running Validation Tests

```bash
# Setup collections with validation
mongosh 00_setup_mongodb.js

# Test validation rules with invalid documents
mongosh 04_bad_inserts.js
```

### Key Validation Rules

| Collection | Validation Rules | Common Violations |
|------------|-----------------|-------------------|
| **farms** | • Positive area values<br>• Valid GeoJSON format<br>• Coordinate ranges | Negative area, invalid coordinates |
| **fields** | • Valid crop types (enum)<br>• Area limits (0.1-1000 ha)<br>• Planting date not future | Unknown crops, extreme areas |
| **gateways** | • EUI format (16 hex chars)<br>• Allowed models<br>• Location required | Invalid EUI, missing location |
| **devices** | • LoRa parameters (SF 7-12)<br>• Bandwidth (125/250/500)<br>• Valid device types | Out-of-spec LoRa config |
| **measurements** | • Moisture 0-100%<br>• Temperature -50 to 60°C<br>• RSSI negative values | Impossible readings |
| **irrigation_schedules** | • Min < Max thresholds<br>• Valid time formats<br>• Schedule types | Inverted thresholds |
| **alerts** | • Severity levels (low/medium/high)<br>• Alert types enum<br>• Message length | Invalid severity |

### Student Exercises

1. **Test Moisture Limits**:
   ```javascript
   // Try inserting moisture > 100%
   db.measurements.insertOne({
     ts: new Date(),
     deviceEui: "A840411234567890",
     soilMoisturePct: 150  // Invalid!
   });
   ```

2. **Validate LoRa Parameters**:
   ```javascript
   // Invalid spreading factor
   db.devices.insertOne({
     deviceEui: "A840411234567890",
     loraConfig: {
       spreadingFactor: 15,  // Must be 7-12
       bandwidth: 125
     }
   });
   ```

3. **Check Agricultural Constraints**:
   ```javascript
   // Negative farm area
   db.farms.insertOne({
     farmName: "Test Farm",
     totalAreaHa: -50  // Invalid!
   });
   ```

### Understanding Validation Errors

When validation fails, MongoDB provides detailed error messages:

```javascript
{
  "errInfo": {
    "failingDocumentId": ObjectId("..."),
    "details": {
      "operatorName": "$jsonSchema",
      "schemaRulesNotSatisfied": [...]
    }
  }
}
```

## Sample Scenarios

The simulation generates realistic agricultural patterns:

- **Daily cycles**: Moisture decreases during day, stabilizes at night
- **Irrigation events**: Scheduled watering increases moisture levels
- **Weather impacts**: Rain events affect all fields in an area
- **Sensor issues**: Battery depletion, signal loss scenarios
- **Alert conditions**: Low moisture warnings, frost alerts

## Query Exercises

The lab includes 15+ queries covering:

1. Current moisture levels by field
2. Fields requiring irrigation
3. Sensor battery status monitoring
4. Daily moisture averages with moving windows
5. Irrigation effectiveness analysis
6. Alert frequency by type and severity
7. Crop-specific moisture compliance
8. Field productivity metrics
9. Sensor reliability statistics
10. Water usage optimization

## Extensions

Possible enhancements for advanced learning:

- Weather data integration
- Predictive irrigation scheduling
- Multi-depth moisture profiling
- Crop yield correlation
- Water conservation metrics
- Cost optimization models

## Notes

- Soil moisture changes gradually (minutes/hours, not seconds)
- LoRaWAN has specific constraints (data rate, battery life)
- Agricultural decisions are based on trends, not single readings
- Different crops have different moisture requirements
- Soil type affects water retention and sensor readings