# Cold Chain Monitoring System Lab

## Overview

This lab implements a comprehensive cold chain monitoring system for temperature-controlled logistics. You'll work with time-series data, adaptive sampling, real-time alerts, and compliance reporting for pharmaceutical and food supply chains.

**Domain**: Logistics & Supply Chain
**Difficulty**: Intermediate
**Duration**: 2-3 hours
**Database**: `coldchain_db`

## Learning Objectives

By completing this lab, you will:

1. Design time-series collections for high-frequency sensor data
2. Implement adaptive sampling strategies based on temperature deviations
3. Build event-driven alerting systems for compliance violations
4. Create geospatial queries for asset and route tracking
5. Develop aggregation pipelines for compliance reporting
6. Understand cold chain logistics and temperature monitoring

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for enhanced time-series features)
- Python 3.8+ with pymongo
- Basic understanding of:
  - Time-series data concepts
  - IoT sensor systems
  - Supply chain logistics
  - Temperature-controlled storage

## Lab Structure

```
cold-chain-monitoring-mongodb/
├── lab.json                     # Lab metadata and configuration
├── README.md                    # This file
├── DATABASE.md                  # Database design documentation
├── 00_setup_mongodb.js          # Database and collection setup
├── 01_seed_data.py              # Master data seeding
├── 02_simulate_telemetry.py     # Time-series data simulation
├── 03_queries_exam.js           # Query exercises
└── 04_bad_inserts.js            # Schema validation examples
```

## Quick Start

### Step 1: Setup Database
```bash
# Using MongoDB shell
mongosh < 00_setup_mongodb.js

# Or using the lab runner
python ../../scripts/lab.py setup cold-chain-monitoring-mongodb
```

### Step 2: Seed Master Data
```bash
# Seed assets, sensors, and initial data
python 01_seed_data.py

# Or using the lab runner
python ../../scripts/lab.py seed cold-chain-monitoring-mongodb
```

### Step 3: Generate Time-Series Data
```bash
# Run 1-hour simulation (generates ~1000 measurements)
python 02_simulate_telemetry.py --hours 1

# Run 24-hour simulation for more data
python 02_simulate_telemetry.py --hours 24

# Use specific seed for reproducible results
python 02_simulate_telemetry.py --hours 4 --seed 42
```

### Step 4: Complete Query Exercises
```bash
# Open in MongoDB shell
mongosh coldchain_db < 03_queries_exam.js

# Or work through queries interactively
mongosh coldchain_db
```

### Step 5: Test Schema Validation
```bash
# See validation rules in action
mongosh coldchain_db < 04_bad_inserts.js
```

## System Architecture

### Collections Overview

1. **assets** - Refrigerators, freezers, trucks, containers
2. **sensors** - IoT devices monitoring temperature, humidity, doors
3. **measurements** - Time-series telemetry data
4. **events** - Operational events (door opens, power failures)
5. **routes** - Transport tracking for mobile assets
6. **alerts** - Real-time alerts and escalations

### Data Flow
```
Physical Assets
    ↓
IoT Sensors → Measurements (every 30s to 5min)
    ↓
Adaptive Sampling (increases frequency on deviation)
    ↓
Event Detection (door opens, excursions)
    ↓
Alert Generation (threshold violations)
    ↓
Compliance Reports
```

## Key Concepts

### 1. Adaptive Sampling
The system automatically adjusts measurement frequency based on conditions:

```python
# From 02_simulate_telemetry.py
if deviation > 2.0:
    return "alarm"      # 30-second intervals
elif deviation > 1.0:
    return "rapid"      # 1-minute intervals
elif deviation > 0.5:
    return "adaptive"   # 2-minute intervals
else:
    return "normal"     # 5-minute intervals
```

### 2. Time-Series Collection
Optimized storage for sensor data:

```javascript
db.createCollection("measurements", {
    timeseries: {
        timeField: "timestamp",
        metaField: "meta",
        granularity: "seconds"
    }
})
```

### 3. Temperature Ranges
Each asset has defined temperature requirements:

```javascript
{
  temperatureRange: {
    min: 2.0,     // Minimum safe temperature
    max: 8.0,     // Maximum safe temperature
    optimal: 5.0  // Target temperature
  }
}
```

### 4. Event Types
System tracks various operational events:
- `door_open` / `door_close` - Access monitoring
- `temperature_excursion` - Limit violations
- `power_failure` / `power_restore` - Equipment issues
- `route_start` / `route_end` - Transport tracking

## Query Exercises

The lab includes 8 comprehensive query exercises:

1. **Current Status Dashboard** - Real-time asset monitoring
2. **Temperature Excursion Report** - Compliance violations
3. **Adaptive Sampling Analysis** - Sampling mode statistics
4. **Route Temperature Analysis** - Transport monitoring
5. **Door Open Analysis** - Access pattern insights
6. **Alert Statistics** - Alert frequency and severity
7. **Battery Monitoring** - Sensor maintenance needs
8. **Compliance Summary** - 24-hour compliance metrics

## Sample Queries

### Get Current Temperature for All Assets
```javascript
db.measurements.aggregate([
  { $sort: { timestamp: -1 } },
  { $group: {
    _id: "$meta.assetId",
    currentTemp: { $first: "$temperature" },
    lastReading: { $first: "$timestamp" }
  }},
  { $lookup: {
    from: "assets",
    localField: "_id",
    foreignField: "assetId",
    as: "asset"
  }}
])
```

### Find Temperature Excursions
```javascript
db.events.find({
  eventType: "temperature_excursion",
  severity: { $in: ["warning", "critical"] },
  timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
})
```

### Calculate Route Statistics
```javascript
db.measurements.aggregate([
  { $match: { "meta.routeId": "RT00000001" } },
  { $group: {
    _id: "$meta.routeId",
    avgTemp: { $avg: "$temperature" },
    maxTemp: { $max: "$temperature" },
    minTemp: { $min: "$temperature" },
    readings: { $sum: 1 }
  }}
])
```

## Advanced Features

### 1. Geospatial Queries
Find assets near a location:
```javascript
db.assets.find({
  "location.coordinates": {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.935242, 40.730610] },
      $maxDistance: 5000  // 5km radius
    }
  }
})
```

### 2. Time-Series Windowing
Analyze trends over time windows:
```javascript
db.measurements.aggregate([
  { $match: {
    "meta.assetId": "FRG000001",
    timestamp: { $gte: new Date(Date.now() - 3600000) }
  }},
  { $setWindowFields: {
    sortBy: { timestamp: 1 },
    output: {
      movingAvg: {
        $avg: "$temperature",
        window: { documents: [-10, 0] }
      }
    }
  }}
])
```

### 3. Compliance Reporting
Generate audit reports:
```javascript
db.events.aggregate([
  { $match: {
    eventType: "temperature_excursion",
    timestamp: {
      $gte: ISODate("2024-01-01"),
      $lt: ISODate("2024-02-01")
    }
  }},
  { $group: {
    _id: {
      asset: "$assetId",
      severity: "$severity"
    },
    count: { $sum: 1 },
    totalDuration: { $sum: "$details.duration_seconds" }
  }}
])
```

## Performance Tips

1. **Use Time-Series Collections**: Automatic compression and optimization
2. **Batch Inserts**: Insert measurements in batches of 1000
3. **Index Patterns**: Always query with assetId + timestamp
4. **Aggregation Pipelines**: Use $match early to reduce dataset
5. **Covered Queries**: Project only needed fields

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Reduce simulation duration
   - Decrease sampling frequency
   - Add memory limits to aggregations

2. **Slow Queries**
   - Check index usage with `.explain()`
   - Add compound indexes for common patterns
   - Use time bounds in queries

3. **Schema Validation Errors**
   - Review `04_bad_inserts.js` for examples
   - Check data types and ranges
   - Verify enum values

### Reset Database
```bash
# Drop and recreate everything
mongosh coldchain_db --eval "db.dropDatabase()"
mongosh < 00_setup_mongodb.js
python 01_seed_data.py
```

## Real-World Applications

This lab simulates scenarios used in:

- **Pharmaceutical Distribution** - Vaccine and medicine storage
- **Food Supply Chain** - Perishable goods transport
- **Chemical Logistics** - Hazardous material monitoring
- **Healthcare** - Blood bank and organ transport
- **Research** - Laboratory sample storage

## Extensions

Try these additional challenges:

1. **Predictive Alerts**: Implement temperature trend prediction
2. **Multi-Zone Monitoring**: Add multiple sensors per asset
3. **Energy Efficiency**: Track power consumption patterns
4. **Route Optimization**: Find optimal transport routes
5. **Blockchain Integration**: Add immutable compliance records

## Resources

- [MongoDB Time Series Documentation](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [Schema Validation Guide](https://www.mongodb.com/docs/manual/core/schema-validation/)
- [Geospatial Queries](https://www.mongodb.com/docs/manual/geospatial-queries/)
- [Aggregation Pipeline](https://www.mongodb.com/docs/manual/aggregation/)

## Support

For issues or questions:
1. Check the `DATABASE.md` for detailed schema documentation
2. Review error messages in schema validation
3. Use `.explain()` to debug query performance
4. Refer to MongoDB documentation for advanced features