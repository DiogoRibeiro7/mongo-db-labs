# Agricultural Pest & Disease Risk Scoring System Lab

## Overview

This lab implements a comprehensive agricultural monitoring system for pest and disease risk assessment across multiple farms. The system tracks environmental conditions (temperature, humidity, rainfall, leaf wetness) and pest populations to calculate risk scores and provide actionable management recommendations.

**Domain**: Agriculture & Precision Farming
**Difficulty**: Intermediate
**Duration**: 2-3 hours
**Database**: `agrimonitor_db`

## Learning Objectives

By completing this lab, you will:

1. Design time-series collections for agricultural monitoring
2. Implement risk scoring algorithms for pest/disease management
3. Build correlation analysis between weather and infestations
4. Create spray recommendation systems
5. Develop trend analysis for risk patterns
6. Analyze multi-farm data aggregations

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series features)
- Python 3.8+ with pymongo, numpy
- Basic understanding of:
  - Agricultural practices
  - Pest management concepts
  - Weather impacts on crops
  - Time-series data

## Lab Structure

```
pest-disease-risk-scoring/
├── lab.json                      # Lab metadata and configuration
├── README.md                     # This file
├── DATABASE.md                   # Database design documentation
├── 00_setup_mongodb.js           # Database and collection setup
├── 01_seed_farms.py              # Multi-regional farm seeding
├── 02_simulate_conditions.py     # Environmental and risk simulation
├── 03_queries_exam.js            # Query exercises
└── 04_bad_inserts.js             # Schema validation examples
```

## Quick Start

### Step 1: Setup Database

```bash
# Using MongoDB shell
mongosh < 00_setup_mongodb.js

# Or using the lab runner
python ../../scripts/lab.py setup pest-disease-risk-scoring
```

### Step 2: Seed Farms and Infrastructure

```bash
# Seed multi-regional farms with sensors
python 01_seed_farms.py

# Or using the lab runner
python ../../scripts/lab.py seed pest-disease-risk-scoring
```

### Step 3: Simulate Environmental Conditions

```bash
# Run 1-hour simulation (default)
python 02_simulate_conditions.py

# Run 24-hour simulation with 30-minute intervals
python 02_simulate_conditions.py --hours 24 --interval 30

# Run 7-day intensive simulation
python 02_simulate_conditions.py --hours 168 --interval 60 --intensity high
```

### Step 4: Run Query Exercises

```bash
# Execute all queries
mongosh agrimonitor_db < 03_queries_exam.js

# Or work through queries interactively
mongosh agrimonitor_db
```

### Step 5: Test Schema Validation

```bash
# See validation rules in action
mongosh agrimonitor_db < 04_bad_inserts.js
```

## System Architecture

### Collections Overview

1. **farms** - Multi-regional agricultural operations
2. **fields** - Individual cultivation areas with crops
3. **sensors** - Weather stations, leaf wetness sensors, pest traps
4. **measurements** - Time-series sensor readings
5. **risk_assessments** - Calculated risk scores with factors
6. **events** - Spray recommendations and risk alerts

### Data Flow

```
Environmental Sensors → Measurements
         ↓
    Risk Calculator → Risk Assessments
         ↓
    Threshold Check → Events (Alerts/Recommendations)
         ↓
    Management Actions → Field Updates
```

## Key Concepts

### 1. Risk Score Calculation (0-100)

The risk score uses weighted environmental factors:

```javascript
Risk Score =
    (Leaf Wetness × 30%) +      // Disease pressure
    (Temperature × 20%) +         // Pathogen development
    (Humidity × 20%) +           // Spore germination
    (Rainfall × 15%) +           // Spread potential
    (Trap Count × 15%)          // Pest pressure
```

### 2. Risk Categories

- **LOW (0-30)**: Routine monitoring
- **MODERATE (31-50)**: Increased vigilance
- **HIGH (51-70)**: Prepare for intervention
- **CRITICAL (71-100)**: Immediate action required

### 3. Leaf Wetness Duration (LWD)

Critical for fungal disease prediction:
- **<4 hours**: Low disease risk
- **4-8 hours**: Moderate risk
- **8-12 hours**: High risk
- **>12 hours**: Critical - immediate fungicide needed

### 4. Economic Thresholds

Pest management decisions based on:
```
Action Threshold = (Cost of Control) / (Value of Crop × Damage per Pest)
```

### 5. Regional Climate Patterns

The simulation includes four distinct regions:

- **California Central Valley**: Mediterranean climate, grapes/citrus
- **Iowa Corn Belt**: Continental climate, corn/soybeans
- **Punjab, India**: Subtropical, rice/wheat
- **Queensland, Australia**: Subtropical/tropical, sugarcane/cotton

## Query Exercises

The lab includes 8 comprehensive query exercises:

1. **Top Risk Plots** - Identify highest-risk fields for immediate intervention
2. **Risk Trend Analysis** - Track 7-day patterns by region
3. **Rainfall Correlation** - Analyze precipitation impact on disease risk
4. **Pest Population Dynamics** - Monitor trap counts and trends
5. **Critical Events Summary** - Review spray recommendations
6. **Leaf Wetness Analysis** - Evaluate disease conditions
7. **Farm Performance** - Compare IPM vs conventional management
8. **Predictive Analysis** - 48-hour risk forecast

## Sample Queries

### Get Current High-Risk Fields

```javascript
db.risk_assessments.aggregate([
  { $match: {
    assessmentTime: { $gte: new Date(Date.now() - 24*60*60*1000) },
    riskScore: { $gte: 60 }
  }},
  { $sort: { riskScore: -1 } },
  { $limit: 10 }
])
```

### Analyze Rainfall Impact

```javascript
db.measurements.aggregate([
  { $match: {
    sensorType: "weather_station",
    "data.rainfall": { $gt: 0 }
  }},
  { $group: {
    _id: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } },
    totalRainfall: { $sum: "$data.rainfall" }
  }}
])
```

### Track Pest Populations

```javascript
db.measurements.find({
  sensorType: "pest_trap",
  "data.trapCount": { $gte: 20 },
  timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
}).sort({ "data.trapCount": -1 })
```

## Simulation Features

### Environmental Modeling

1. **Weather Patterns**
   - Diurnal temperature variation
   - Seasonal adjustments
   - Regional climate differences
   - Rainfall events

2. **Pest Dynamics**
   - Population growth models
   - Weather influence
   - Migration patterns
   - Economic thresholds

3. **Disease Development**
   - Infection periods
   - Sporulation conditions
   - Spread modeling
   - Host susceptibility

### Risk Factors

| Factor | Weight | Critical Threshold | Impact |
|--------|--------|-------------------|---------|
| Leaf Wetness | 30% | >10 hours | Fungal diseases |
| Temperature | 20% | 18-28°C | Pathogen optimal |
| Humidity | 20% | >75% | Spore germination |
| Rainfall | 15% | >10mm/day | Disease spread |
| Trap Count | 15% | >20/trap | Pest outbreak |

## Management Recommendations

### IPM (Integrated Pest Management) Approach

1. **Prevention**
   - Resistant varieties
   - Crop rotation
   - Sanitation

2. **Monitoring**
   - Regular scouting
   - Trap monitoring
   - Weather tracking

3. **Intervention**
   - Economic thresholds
   - Targeted applications
   - Biological controls

4. **Evaluation**
   - Treatment efficacy
   - Resistance monitoring
   - Cost-benefit analysis

## Performance Optimization

### Time-Series Benefits
- 70% storage reduction
- Automatic compression
- Optimized queries
- Built-in aggregation

### Query Performance
```javascript
// Use covered queries
db.risk_assessments.find(
  { fieldId: "FLD00000001", riskScore: { $gte: 70 } },
  { _id: 0, riskScore: 1, assessmentTime: 1 }
)

// Leverage indexes
db.measurements.find({
  "meta.fieldId": "FLD00000001",
  timestamp: { $gte: new Date(Date.now() - 86400000) }
})
```

## Common Issues & Solutions

### Issue 1: High Risk Scores
**Symptoms**: Consistently high risk across fields
**Causes**: Extended wet periods, high pest pressure
**Solution**: Review thresholds, implement preventive treatments

### Issue 2: Missing Sensor Data
**Symptoms**: Gaps in measurements
**Causes**: Connectivity issues, sensor failures
**Solution**: Check sensor status, verify network connectivity

### Issue 3: False Alerts
**Symptoms**: Alerts without actual risk
**Causes**: Sensor drift, incorrect thresholds
**Solution**: Calibrate sensors, adjust risk parameters

## Reset Database

```bash
# Complete reset
mongosh agrimonitor_db --eval "db.dropDatabase()"
mongosh < 00_setup_mongodb.js
python 01_seed_farms.py
```

## Real-World Applications

This lab simulates systems used by:

- **Precision Agriculture Companies**: John Deere, Trimble, Climate Corp
- **Crop Consultants**: IPM advisors, agronomists
- **Research Institutions**: Universities, USDA, CGIAR
- **Farmers**: Progressive growers using data-driven decisions
- **Agricultural Cooperatives**: Regional pest monitoring networks

## Disease & Pest Models

### Disease Risk Models

1. **Powdery Mildew** (Grapes)
   - Temperature: 20-27°C optimal
   - Humidity: 40-100%
   - No free water needed

2. **Late Blight** (Tomatoes/Potatoes)
   - Temperature: 10-25°C
   - Humidity: >90%
   - Leaf wetness: >10 hours

3. **Rust** (Wheat)
   - Temperature: 15-25°C
   - Humidity: >85%
   - Dew period: >6 hours

### Pest Population Models

1. **Aphids**
   - Threshold: 50/plant
   - Generation time: 7-10 days
   - Temperature: 18-25°C optimal

2. **Whitefly**
   - Threshold: 10/leaf
   - Generation time: 21-30 days
   - Temperature: 25-30°C optimal

## Extensions

Try these additional challenges:

1. **Machine Learning**: Train models on historical risk data
2. **Weather API**: Integrate forecast data for predictions
3. **Image Analysis**: Process trap photos for counting
4. **Mobile App**: Build field scouting application
5. **Drone Integration**: Add aerial monitoring data
6. **Yield Impact**: Correlate risk with harvest data

## Agricultural Formulas

### Degree Days (DD)
```
DD = (Tmax + Tmin)/2 - Tbase
Used for: Pest development, crop growth stages
```

### Disease Severity Index (DSI)
```
DSI = Σ(Rating × Plants in category) / (Total plants × Max rating) × 100
```

### Economic Injury Level (EIL)
```
EIL = Control Cost / (Market Value × Damage × Control Efficacy)
```

## Compliance & Certifications

The system tracks compliance with:

- **Organic Standards**: USDA NOP, EU Organic
- **GlobalGAP**: Good Agricultural Practices
- **IPM Certification**: Regional programs
- **Pesticide Regulations**: REI, PHI, MRL compliance

## Resources

- [MongoDB Time-Series](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [IPM Guidelines](https://ipm.ucanr.edu/)
- [Disease Models](https://uspest.org/risk/models)
- [FAO Pest Management](http://www.fao.org/pest-and-pesticide-management/)

## Support

For issues or questions:
1. Check the `DATABASE.md` for schema details
2. Review error messages in validation
3. Use `.explain()` to debug queries
4. Monitor risk trends for patterns