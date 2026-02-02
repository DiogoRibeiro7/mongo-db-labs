# Smart Grid Energy Monitoring System Lab

## Overview

This lab implements a comprehensive energy monitoring system for smart grids, tracking household and building energy consumption with smart meters, time-of-use tariffs, peak demand alerts, and automated billing. You'll work with time-series electrical data including kWh consumption, voltage, current, and power factor measurements.

**Domain**: Energy & Utilities
**Difficulty**: Intermediate
**Duration**: 2-3 hours
**Database**: `energygrid_db`

## Learning Objectives

By completing this lab, you will:

1. Design time-series collections for energy consumption data
2. Implement time-of-use tariff calculations
3. Build peak demand detection and alerting
4. Create daily consumption totals and patterns
5. Develop cost estimation pipelines
6. Analyze power quality metrics

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series features)
- Python 3.8+ with pymongo
- Basic understanding of:
  - Electrical systems (voltage, current, power)
  - Utility billing concepts
  - Time-series data
  - Energy markets

## Lab Structure

```
energy-monitoring-smart-grid/
├── lab.json                      # Lab metadata and configuration
├── README.md                     # This file
├── DATABASE.md                   # Database design documentation
├── 00_setup_mongodb.js           # Database and collection setup
├── 01_seed_infrastructure.py     # Infrastructure data seeding
├── 02_simulate_consumption.py    # Energy consumption simulation
├── 03_queries_exam.js            # Query exercises
└── 04_bad_inserts.js             # Schema validation examples
```

## Quick Start

### Step 1: Setup Database
```bash
# Using MongoDB shell
mongosh < 00_setup_mongodb.js

# Or using the lab runner
python ../../scripts/lab.py setup energy-monitoring-smart-grid
```

### Step 2: Seed Infrastructure
```bash
# Seed buildings, meters, and tariffs
python 01_seed_infrastructure.py

# Or using the lab runner
python ../../scripts/lab.py seed energy-monitoring-smart-grid
```

### Step 3: Simulate Energy Consumption
```bash
# Run 1-hour simulation (15-minute intervals)
python 02_simulate_consumption.py --hours 1

# Run 24-hour simulation with 15-minute readings
python 02_simulate_consumption.py --hours 24 --interval 15

# Run week-long simulation
python 02_simulate_consumption.py --hours 168 --interval 60
```

### Step 4: Run Query Exercises
```bash
# Open in MongoDB shell
mongosh energygrid_db < 03_queries_exam.js

# Or work through queries interactively
mongosh energygrid_db
```

### Step 5: Test Schema Validation
```bash
# See validation rules in action
mongosh energygrid_db < 04_bad_inserts.js
```

## System Architecture

### Collections Overview

1. **buildings** - Residential, commercial, and industrial buildings
2. **meters** - Smart meter devices and configurations
3. **tariffs** - Pricing plans (flat, tiered, time-of-use)
4. **readings** - Time-series energy measurements
5. **events** - Peak demand, outages, power quality issues
6. **bills** - Monthly billing and invoicing

### Data Flow
```
Smart Meters (15-min intervals)
    ↓
Gateway → Time-Series Readings
    ↓
Peak Detection → Events
    ↓
Cost Calculation → Bills
    ↓
Analytics & Reporting
```

## Key Concepts

### 1. Electrical Parameters

```javascript
{
  // Energy
  kWhConsumed: 12.5,        // Kilowatt-hours consumed
  kWDemand: 50.2,           // Current power demand (kW)

  // Electrical measurements
  voltage: 239.5,           // Volts (target: 240V ±10%)
  current: 209.8,           // Amperes
  frequency: 59.98,         // Hz (target: 60Hz ±0.5Hz)

  // Power components
  activePower: 50.2,        // kW (real power doing work)
  reactivePower: 19.3,      // kVAR (reactive power)
  apparentPower: 54.6,      // kVA (total power)
  powerFactor: 0.92         // Efficiency (target: >0.90)
}
```

### 2. Time-of-Use Tariffs

Different rates for different times:
- **Peak Hours** (4-9 PM): $0.20/kWh - Highest demand
- **Shoulder Hours** (7 AM-4 PM, 9-11 PM): $0.12/kWh - Moderate
- **Off-Peak Hours** (11 PM-7 AM): $0.08/kWh - Lowest demand

### 3. Demand Charges

Commercial/Industrial customers pay for peak demand:
```
Monthly Demand Charge = Peak kW × Demand Rate
Example: 275 kW × $15/kW = $4,125
```

### 4. Power Factor

Efficiency measure (Real Power / Apparent Power):
- **>0.95**: Excellent (no penalty)
- **0.90-0.95**: Good
- **<0.90**: Poor (penalty applied)

### 5. Building Types and Patterns

- **Residential**: Morning (6-9 AM) and evening (6-10 PM) peaks
- **Commercial**: Business hours peak (9 AM-5 PM)
- **Industrial**: 24/7 base load with shift patterns

## Query Exercises

The lab includes 8 comprehensive query exercises:

1. **Grid Status Overview** - Current demand by building type
2. **Daily Consumption Totals** - 24-hour usage and costs
3. **Peak Demand Intervals** - Identify highest load periods
4. **Time-of-Use Analysis** - Consumption by pricing period
5. **Power Quality Metrics** - Voltage and frequency issues
6. **Energy Efficiency** - Performance by building class
7. **Outage Impact** - Event analysis and costs
8. **Billing Summary** - Revenue and collection rates

## Sample Queries

### Get Current Grid Load
```javascript
db.readings.aggregate([
  { $match: {
    timestamp: { $gte: new Date(Date.now() - 60*60*1000) }
  }},
  { $group: {
    _id: null,
    totalDemandKW: { $sum: "$kWDemand" },
    avgVoltage: { $avg: "$voltage" },
    avgPowerFactor: { $avg: "$powerFactor" }
  }}
])
```

### Calculate Daily Energy Cost
```javascript
db.readings.aggregate([
  { $match: {
    "meta.buildingId": "BLD00000001",
    timestamp: {
      $gte: ISODate("2024-01-30T00:00:00Z"),
      $lt: ISODate("2024-01-31T00:00:00Z")
    }
  }},
  { $group: {
    _id: { $hour: "$timestamp" },
    hourlyKWh: { $sum: "$kWhConsumed" }
  }},
  { $addFields: {
    // Apply TOU rates
    rate: {
      $switch: {
        branches: [
          { case: { $and: [{ $gte: ["$_id", 16] }, { $lte: ["$_id", 21] }] },
            then: 0.20 },  // Peak
          { case: { $or: [{ $lt: ["$_id", 7] }, { $gt: ["$_id", 23] }] },
            then: 0.08 }   // Off-peak
        ],
        default: 0.12      // Shoulder
      }
    }
  }},
  { $group: {
    _id: null,
    totalCost: { $sum: { $multiply: ["$hourlyKWh", "$rate"] } }
  }}
])
```

### Find Peak Demand Events
```javascript
db.events.find({
  eventType: "peak_demand",
  severity: "critical",
  timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
}).sort({ "details.peakValue": -1 })
```

## Advanced Features

### 1. Power Quality Monitoring
```javascript
// Detect voltage issues
db.readings.aggregate([
  { $match: {
    $or: [
      { voltage: { $lt: 216 } },  // Sag (<90% of 240V)
      { voltage: { $gt: 264 } }   // Spike (>110% of 240V)
    ]
  }},
  { $group: {
    _id: "$meta.meterId",
    incidents: { $sum: 1 },
    avgVoltage: { $avg: "$voltage" }
  }}
])
```

### 2. Demand Response
Automatically reduce load during peak:
```javascript
// Identify candidates for load shedding
db.buildings.aggregate([
  { $lookup: {
    from: "readings",
    localField: "buildingId",
    foreignField: "meta.buildingId",
    as: "currentLoad"
  }},
  { $match: {
    "characteristics.hasBackupPower": true,
    "currentLoad.kWDemand": { $gt: 100 }
  }}
])
```

### 3. Solar Generation Analysis
For buildings with solar panels:
```javascript
db.readings.aggregate([
  { $match: {
    "meta.meterType": "solar",
    solarGeneration: { $exists: true }
  }},
  { $group: {
    _id: { $hour: "$timestamp" },
    avgGeneration: { $avg: "$solarGeneration" },
    totalGenerated: { $sum: "$solarGeneration" }
  }},
  { $sort: { _id: 1 } }
])
```

## Simulation Parameters

### Consumption Patterns
The simulator models realistic patterns:
- **Temperature Effect**: ±20% based on weather
- **Occupancy Effect**: Reduced consumption when vacant
- **Equipment Cycling**: HVAC and industrial equipment patterns
- **Random Variation**: ±5% natural fluctuation

### Event Generation
- **Peak Demand**: 1% chance per interval for commercial
- **Voltage Issues**: 0.2% chance per reading
- **Power Outages**: 0.01% chance (affects multiple buildings)
- **Meter Issues**: 0.01% chance

## Performance Tips

1. **Use Time-Series Collections**: 70% storage reduction
2. **Batch Inserts**: Insert readings in batches of 1000
3. **Index Strategy**: Filter by building/meter first, then time
4. **Aggregation**: Use $match early to reduce dataset
5. **Archival**: Consider TTL indexes for old readings

## Troubleshooting

### Common Issues

1. **High Demand Charges**
   - Check peak demand times
   - Review contracted maximum
   - Consider load shifting

2. **Poor Power Factor**
   - Industrial equipment often the cause
   - Add power factor correction
   - Check for harmonic distortion

3. **Missing Readings**
   - Check meter connectivity
   - Review signal strength
   - Verify gateway status

### Reset Database
```bash
# Drop and recreate everything
mongosh energygrid_db --eval "db.dropDatabase()"
mongosh < 00_setup_mongodb.js
python 01_seed_infrastructure.py
```

## Real-World Applications

This lab simulates systems used by:

- **Utility Companies**: PG&E, ConEd, Duke Energy
- **Smart Cities**: Barcelona, Singapore, Copenhagen
- **Industrial Parks**: Manufacturing facilities
- **Commercial Buildings**: Office towers, shopping centers
- **Residential Complexes**: Apartment buildings, condos
- **Renewable Energy**: Solar farms, wind installations

## Energy Formulas

### Power Triangle
```
Apparent Power² = Active Power² + Reactive Power²
S² = P² + Q²
```

### Power Factor
```
Power Factor = Active Power / Apparent Power
PF = P / S = cos(φ)
```

### Energy Cost
```
Cost = Σ(Consumption × Rate) + Demand Charge + Fixed Charge + Taxes
```

### Load Factor
```
Load Factor = Average Load / Peak Load
(Higher is better - indicates steady consumption)
```

## Extensions

Try these additional challenges:

1. **Predictive Analytics**: Forecast next day's consumption
2. **Anomaly Detection**: Identify unusual usage patterns
3. **Dynamic Pricing**: Implement real-time pricing
4. **Battery Storage**: Add battery management for peak shaving
5. **Carbon Tracking**: Calculate CO₂ emissions

## Tariff Comparison

| Type | Best For | Pros | Cons |
|------|----------|------|------|
| Flat | Stable usage | Predictable | No savings incentive |
| Tiered | Low users | Rewards conservation | Penalizes high use |
| Time-of-Use | Flexible users | Off-peak savings | Peak penalties |
| Dynamic | Large users | Market rates | Price volatility |

## Grid Metrics

### Key Performance Indicators
- **System Load Factor**: >70% (efficiency)
- **Power Factor**: >0.90 (quality)
- **Voltage Regulation**: ±10% (stability)
- **Frequency Regulation**: ±0.5Hz (reliability)
- **Collection Rate**: >95% (revenue)

## Resources

- [MongoDB Time Series](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [Smart Grid Standards](https://www.nist.gov/smartgrid)
- [Energy Information Administration](https://www.eia.gov/)
- [Power Quality Standards](https://www.ieee.org/)

## Support

For issues or questions:
1. Check the `DATABASE.md` for detailed schema documentation
2. Review error messages in schema validation
3. Use `.explain()` to debug query performance
4. Monitor power factor and demand charges