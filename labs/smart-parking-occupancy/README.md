# Smart Parking Occupancy System Lab

## Overview

This lab implements a comprehensive smart parking management system using IoT sensors (magnetometer, ultrasonic, infrared) to track real-time occupancy, detect violations, and optimize urban parking resources. You'll work with confidence-based sensor readings, zone analytics, and violation enforcement.

**Domain**: Smart City & IoT
**Difficulty**: Intermediate
**Duration**: 2-3 hours
**Database**: `smartparking_db`

## Learning Objectives

By completing this lab, you will:

1. Design IoT sensor data models with confidence scoring
2. Implement parking violation detection logic
3. Build zone-based occupancy analytics
4. Create hourly utilization reports
5. Develop revenue optimization queries
6. Understand smart city parking infrastructure

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series features)
- Python 3.8+ with pymongo
- Basic understanding of:
  - IoT sensor networks
  - Smart city concepts
  - Time-series data
  - Geospatial queries

## Lab Structure

```
smart-parking-occupancy/
├── lab.json                      # Lab metadata and configuration
├── README.md                     # This file
├── DATABASE.md                   # Database design documentation
├── 00_setup_mongodb.js           # Database and collection setup
├── 01_seed_infrastructure.py     # Infrastructure data seeding
├── 02_simulate_occupancy.py      # Occupancy simulation
├── 03_queries_exam.js            # Query exercises
└── 04_bad_inserts.js             # Schema validation examples
```

## Quick Start

### Step 1: Setup Database
```bash
# Using MongoDB shell
mongosh < 00_setup_mongodb.js

# Or using the lab runner
python ../../scripts/lab.py setup smart-parking-occupancy
```

### Step 2: Seed Infrastructure
```bash
# Seed zones, spots, and sensors
python 01_seed_infrastructure.py

# Or using the lab runner
python ../../scripts/lab.py seed smart-parking-occupancy
```

### Step 3: Simulate Parking Activity
```bash
# Run 1-hour simulation (quick test)
python 02_simulate_occupancy.py --hours 1

# Run 24-hour simulation (full day pattern)
python 02_simulate_occupancy.py --hours 24

# Custom simulation with 2-minute steps
python 02_simulate_occupancy.py --hours 8 --step-minutes 2
```

### Step 4: Run Query Exercises
```bash
# Open in MongoDB shell
mongosh smartparking_db < 03_queries_exam.js

# Or work through queries interactively
mongosh smartparking_db
```

### Step 5: Test Schema Validation
```bash
# See validation rules in action
mongosh smartparking_db < 04_bad_inserts.js
```

## System Architecture

### Collections Overview

1. **zones** - Parking areas (street, garage, lot)
2. **parking_spots** - Individual parking spaces
3. **sensors** - IoT devices (magnetometer, ultrasonic, infrared)
4. **occupancy_readings** - Time-series sensor data with confidence
5. **events** - Occupancy changes, violations, sensor issues
6. **violations** - Parking violations and fines

### Data Flow
```
IoT Sensors (LoRa/NB-IoT)
    ↓
Gateway → Occupancy Readings (with confidence)
    ↓
Event Detection (occupancy_change, overstay)
    ↓
Status Updates → Violations
    ↓
Analytics & Reporting
```

## Key Concepts

### 1. Sensor Types and Confidence

Different sensors provide varying confidence levels:

```javascript
// Magnetometer (most common)
{
  type: "magnetometer",
  confidence: 0.92-0.99,     // High confidence
  detects: "Metal presence"
}

// Ultrasonic
{
  type: "ultrasonic",
  confidence: 0.88-0.96,     // Good confidence
  detects: "Distance/height"
}

// Infrared
{
  type: "infrared",
  confidence: 0.85-0.94,     // Moderate confidence
  detects: "Heat/presence"
}
```

### 2. Binary Occupancy with Confidence Score

Each reading includes:
```javascript
{
  occupied: true,           // Binary status
  confidence: 0.95,        // Probability (0-1)
  status: "occupied",      // Detailed status
  magneticField: 235.5,    // Sensor-specific data
  fieldStrength: 85.5
}
```

### 3. Zone Types and Patterns

Different zones have distinct occupancy patterns:
- **Street Parking**: Peak during business hours (9am-5pm)
- **Shopping Lots**: Peak midday and evenings
- **Garages**: Steady during business hours
- **Transit Lots**: Morning and evening commute peaks

### 4. Violation Types
- `overstay` - Exceeded paid time
- `no_payment` - No valid payment
- `invalid_permit` - Wrong or expired permit
- `wrong_spot_type` - Regular vehicle in disabled spot
- `outside_hours` - Parking outside operating hours

## Query Exercises

The lab includes 8 comprehensive query exercises:

1. **Current Occupancy Overview** - Real-time zone statistics
2. **Hourly Patterns Analysis** - Peak hour identification
3. **Busiest Zones** - Turnover and utilization metrics
4. **Violation Analysis** - Revenue and enforcement stats
5. **Sensor Performance** - Confidence and reliability metrics
6. **Revenue Optimization** - Peak pricing opportunities
7. **Sensor Reliability** - Offline events and maintenance
8. **Zone Dashboard** - Comprehensive performance metrics

## Sample Queries

### Find Available Spots Near Me
```javascript
db.parking_spots.find({
  status: "available",
  "location.coordinates": {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.4194, 37.7749] },
      $maxDistance: 500  // 500 meters
    }
  }
}).limit(10)
```

### Calculate Zone Occupancy Rate
```javascript
db.zones.aggregate([
  { $lookup: {
    from: "parking_spots",
    localField: "zoneId",
    foreignField: "zoneId",
    as: "spots"
  }},
  { $project: {
    name: 1,
    occupancyRate: {
      $multiply: [
        { $divide: [
          { $size: {
            $filter: {
              input: "$spots",
              cond: { $eq: ["$$this.status", "occupied"] }
            }
          }},
          { $size: "$spots" }
        ]},
        100
      ]
    }
  }}
])
```

### Hourly Revenue Analysis
```javascript
db.parking_spots.aggregate([
  { $match: { "currentOccupant": { $exists: true } } },
  { $lookup: {
    from: "zones",
    localField: "zoneId",
    foreignField: "zoneId",
    as: "zone"
  }},
  { $unwind: "$zone" },
  { $group: {
    _id: { $hour: "$currentOccupant.entryTime" },
    totalRevenue: {
      $sum: {
        $multiply: [
          "$zone.pricing.perHour",
          { $divide: [
            { $subtract: [
              "$currentOccupant.paidUntil",
              "$currentOccupant.entryTime"
            ]},
            3600000
          ]}
        ]
      }
    }
  }},
  { $sort: { totalRevenue: -1 } }
])
```

## Advanced Features

### 1. Confidence-Based Decision Making
```javascript
// Only trust high-confidence readings
db.occupancy_readings.find({
  confidence: { $gte: 0.85 },
  timestamp: { $gte: new Date(Date.now() - 3600000) }
})
```

### 2. Sensor Fusion
Combine multiple sensor readings:
```javascript
db.occupancy_readings.aggregate([
  { $match: {
    "meta.spotId": "SPOT00000001",
    timestamp: { $gte: new Date(Date.now() - 60000) }
  }},
  { $group: {
    _id: "$meta.spotId",
    avgConfidence: { $avg: "$confidence" },
    consensusOccupied: {
      $avg: { $cond: ["$occupied", 1, 0] }
    }
  }},
  { $project: {
    finalStatus: {
      $cond: [{ $gte: ["$consensusOccupied", 0.5] }, "occupied", "available"]
    },
    confidence: "$avgConfidence"
  }}
])
```

### 3. Violation Hot Spots
Identify problem areas:
```javascript
db.violations.aggregate([
  { $match: {
    timestamp: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
  }},
  { $group: {
    _id: "$spotId",
    violationCount: { $sum: 1 },
    types: { $addToSet: "$type" },
    totalFines: { $sum: "$fine.amount" }
  }},
  { $match: { violationCount: { $gte: 5 } } },
  { $sort: { violationCount: -1 } }
])
```

## Simulation Parameters

### Demand Patterns
The simulator models realistic parking patterns:
- **Morning Rush** (7-9am): Increasing occupancy
- **Business Hours** (9am-5pm): High occupancy (85-95%)
- **Evening** (5-7pm): Decreasing occupancy
- **Night** (7pm-7am): Low occupancy (10-30%)
- **Weekends**: Different patterns (less business, more shopping)

### Sensor Behavior
- **Reading Frequency**: Every 5 minutes (configurable)
- **Battery Drain**: ~0.1% per hour
- **Offline Rate**: 0.1% chance per hour
- **Confidence Variation**: ±5% based on conditions

## Performance Tips

1. **Use Time-Series Collections**: Automatic compression for readings
2. **Index Patterns**: Always filter by zoneId or spotId first
3. **Batch Operations**: Insert readings in batches of 1000
4. **Aggregation Optimization**: Use $match early in pipelines
5. **Geospatial Queries**: Use 2dsphere indexes with $near

## Troubleshooting

### Common Issues

1. **Low Confidence Readings**
   - Check sensor calibration settings
   - Verify sensor battery levels
   - Review environmental interference

2. **Missing Occupancy Data**
   - Check sensor status (active/offline)
   - Verify gateway connectivity
   - Review event logs for sensor_offline

3. **Incorrect Violations**
   - Verify spot type matches vehicle
   - Check payment records
   - Review grace period settings

### Reset Database
```bash
# Drop and recreate everything
mongosh smartparking_db --eval "db.dropDatabase()"
mongosh < 00_setup_mongodb.js
python 01_seed_infrastructure.py
```

## Real-World Applications

This lab simulates systems used in:

- **Smart Cities**: San Francisco, Barcelona, Singapore
- **Airports**: Real-time parking availability
- **Shopping Centers**: Customer parking management
- **Universities**: Campus parking systems
- **Hospitals**: Patient and staff parking
- **Event Venues**: Dynamic pricing for events

## LoRa Network Architecture

### Why LoRa for Parking?
- **Long Range**: Up to 10km in urban areas
- **Low Power**: 10-year battery life possible
- **Low Cost**: Inexpensive sensors and gateways
- **Deep Penetration**: Works in underground garages
- **Scalable**: Thousands of sensors per gateway

### Network Topology
```
Sensors → LoRa Gateway → Network Server → Application Server → MongoDB
```

## Extensions

Try these additional challenges:

1. **Predictive Availability**: ML model to predict spot availability
2. **Dynamic Pricing**: Adjust rates based on demand
3. **Reservation System**: Allow advance spot booking
4. **Multi-Sensor Fusion**: Combine sensor types for accuracy
5. **Mobile App Integration**: Real-time availability API

## Metrics and KPIs

### Operational Metrics
- **Occupancy Rate**: Percentage of occupied spots
- **Turnover Rate**: Vehicles per spot per day
- **Average Stay Duration**: Time per parking session
- **Violation Rate**: Violations per 100 vehicles

### Financial Metrics
- **Revenue per Spot**: Daily/monthly revenue
- **Collection Rate**: Paid vs issued violations
- **Peak Hour Premium**: Additional revenue from peak pricing
- **Utilization Rate**: Actual vs potential revenue

### Technical Metrics
- **Sensor Uptime**: Percentage online
- **Detection Accuracy**: True vs false positives
- **Network Latency**: Sensor to database time
- **Battery Life**: Days until replacement

## Resources

- [LoRa Alliance](https://lora-alliance.org/)
- [MongoDB Time Series](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [Smart Parking Solutions](https://www.smartparking.com/)
- [IoT Sensor Technologies](https://www.iot-now.com/)

## Support

For issues or questions:
1. Check the `DATABASE.md` for detailed schema documentation
2. Review error messages in schema validation
3. Use `.explain()` to debug query performance
4. Monitor sensor confidence scores for reliability