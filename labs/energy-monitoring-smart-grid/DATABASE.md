# Smart Grid Energy Monitoring Database Design

## Overview

The Smart Grid Energy Monitoring System database (`energygrid_db`) is designed to track household and building energy consumption using smart meters, implement time-of-use tariffs, detect peak demand events, and manage utility billing. The system monitors electrical parameters including kWh consumption, voltage, current, and power factor for residential, commercial, and industrial buildings.

## Key Features

- **Time-Series Energy Data**: High-frequency readings of electrical parameters
- **Multi-Tariff Support**: Flat, tiered, time-of-use, and dynamic pricing
- **Peak Demand Management**: Real-time detection and alerting
- **Power Quality Monitoring**: Voltage, frequency, and power factor tracking
- **Billing Integration**: Automated cost calculation and invoice generation
- **Grid Event Detection**: Outages, voltage issues, and quality problems

## Collections Architecture

### 1. Buildings Collection
**Purpose**: Registry of all monitored buildings and facilities

```javascript
{
  buildingId: "BLD00000001",      // Unique building identifier
  type: "commercial",              // residential|commercial|industrial|mixed
  subType: "office",               // Specific building category
  name: "Office Building 001",
  address: {
    street: "123 Business Blvd",
    city: "San Francisco",
    state: "CA",
    postalCode: "94102",
    country: "USA",
    coordinates: {
      lat: 37.7749,
      lng: -122.4194
    }
  },
  status: "active",                // active|inactive|construction|renovation
  characteristics: {
    floors: 10,
    units: 50,                     // Number of units/tenants
    squareMeters: 5000,
    yearBuilt: 2015,
    energyClass: "B",              // Energy efficiency rating A-G
    hasSolar: true,
    hasBackupPower: true,
    hasEVCharging: true
  },
  occupancy: {
    residents: 0,                  // For residential
    businesses: 50,                // For commercial
    typicalOccupancy: {
      weekday: 500,
      weekend: 50
    }
  },
  contractInfo: {
    accountNumber: "ACC123456",
    tariffPlanId: "TAR1001",
    contractStart: ISODate("2023-01-01"),
    contractEnd: ISODate("2025-12-31"),
    maxDemandKW: 250.0,            // Contracted maximum demand
    voltageLevel: "MV"             // LV|MV|HV
  }
}
```

**Key Design Decisions**:
- Building types determine consumption patterns
- Energy class tracks efficiency improvements
- Contract info links to tariff and billing
- Occupancy patterns for demand prediction

### 2. Meters Collection
**Purpose**: Smart meter devices and configurations

```javascript
{
  meterId: "MTR0000000001",        // Smart meter serial number
  buildingId: "BLD00000001",
  type: "electricity",             // electricity|gas|water|solar|battery
  subType: "three_phase",          // single_phase|three_phase|net_metering
  manufacturer: "Landis+Gyr",
  model: "SM-X5000",
  status: "active",                // active|inactive|faulty|maintenance|replaced
  capabilities: {
    bidirectional: false,          // For solar/battery systems
    remoteDisconnect: true,
    powerQuality: true,            // Advanced measurements
    tamperDetection: true,
    realtimeData: true
  },
  specifications: {
    maxCurrent: 200.0,             // Amperes
    maxVoltage: 480.0,             // Volts
    accuracy: 99.5,                // Percentage
    measurementInterval: 15        // Minutes
  },
  connectivity: {
    protocol: "cellular",          // zigbee|lorawan|cellular|plc|wifi
    lastCommunication: ISODate("2024-01-30T14:30:00Z"),
    signalStrength: -65,           // dBm
    firmwareVersion: "2.3.1"
  },
  calibration: {
    lastCalibrated: ISODate("2023-01-15"),
    nextCalibration: ISODate("2025-01-15"),
    calibrationFactor: 1.002
  }
}
```

**Key Design Decisions**:
- Multiple meter types per building
- Connectivity tracking for reliability
- Calibration for accuracy maintenance
- Firmware tracking for updates

### 3. Tariffs Collection
**Purpose**: Electricity pricing plans and structures

```javascript
{
  tariffId: "TAR0002",
  name: "Residential Time-of-Use",
  type: "time_of_use",             // flat|tiered|time_of_use|dynamic|prepaid
  customerType: "residential",     // residential|commercial|industrial
  description: "TOU rates with peak/off-peak pricing",
  validFrom: ISODate("2023-01-01"),
  validUntil: null,
  rates: {
    currency: "USD",

    // Time-of-use structure
    timeOfUse: {
      peak: {
        hours: [{ start: "16:00", end: "21:00" }],
        pricePerKWh: 0.20
      },
      offPeak: {
        pricePerKWh: 0.08
      },
      shoulder: {
        hours: [
          { start: "07:00", end: "16:00" },
          { start: "21:00", end: "23:00" }
        ],
        pricePerKWh: 0.12
      }
    },

    // Fixed charges
    fixedCharges: {
      monthlyCharge: 12.00,
      connectionCharge: 0.00,
      demandCharge: 15.00          // Per kW for commercial
    },

    // Taxes
    taxes: [
      { name: "State Tax", rate: 0.05 },
      { name: "City Tax", rate: 0.02 }
    ]
  },
  incentives: {
    solarFeedIn: 0.10,             // Solar generation credit
    evCharging: 0.06,              // EV charging discount
    greenEnergy: 0.01               // Renewable energy credit
  },
  penalties: {
    exceededDemand: 25.00,          // Per kW over limit
    powerFactor: 0.05,              // Poor power factor penalty
    latePayment: 0.015              // 1.5% per month
  }
}
```

**Key Design Decisions**:
- Flexible rate structures (flat, tiered, TOU)
- Support for incentives and penalties
- Tax calculation built-in
- Time-based pricing for demand response

### 4. Readings Collection (Time-Series)
**Purpose**: High-frequency energy consumption measurements

```javascript
{
  timestamp: ISODate("2024-01-30T14:30:00Z"),
  meta: {                          // Time-series metadata
    meterId: "MTR0000000001",
    buildingId: "BLD00000001",
    meterType: "electricity",
    readingType: "interval"        // interval|snapshot|cumulative
  },

  // Energy consumption
  kWhConsumed: 12.5,              // Energy consumed in interval
  kWDemand: 50.2,                  // Current demand
  peakKW: 52.1,                    // Peak in interval

  // Electrical parameters
  voltage: 239.5,                  // Volts
  current: 209.8,                  // Amperes
  powerFactor: 0.92,               // 0-1 (ideal is 1)
  frequency: 59.98,                // Hz

  // Power components
  activePower: 50.2,               // kW (real power)
  reactivePower: 19.3,             // kVAR (reactive power)
  apparentPower: 54.6,             // kVA (apparent power)

  // Three-phase details
  phaseVoltages: [239.5, 240.1, 238.9],
  phaseCurrents: [69.8, 70.1, 69.9],
  phaseImbalance: 0.012,           // Percentage

  // Quality metrics
  thd: 0.03,                       // Total harmonic distortion
  signalQuality: 95,               // Percentage

  // Solar generation (if applicable)
  solarGeneration: 15.3,           // kW
  netMetering: -2.8,               // Negative = feeding to grid

  // Meter status
  temperature: 25.3,               // Meter temperature °C
  signalStrength: -65              // dBm
}
```

**Key Design Decisions**:
- Time-series collection for compression
- Complete electrical parameters
- Three-phase support
- Power quality metrics
- Solar generation tracking

### 5. Events Collection
**Purpose**: Grid events, outages, and quality issues

```javascript
{
  eventId: "EVT000000000001",
  eventType: "peak_demand",        // power_outage|peak_demand|voltage_sag|
                                   // voltage_spike|frequency_deviation|meter_failure
  meterId: "MTR0000000001",
  buildingId: "BLD00000001",
  timestamp: ISODate("2024-01-30T16:00:00Z"),
  endTime: ISODate("2024-01-30T17:30:00Z"),
  severity: "warning",             // info|warning|critical|emergency
  details: {
    duration: 5400,                // Seconds
    peakValue: 275.5,              // kW
    thresholdExceeded: 250.0,      // Contracted max
    estimatedCost: 412.50,         // Demand charge penalty
    affectedUnits: 50
  },
  location: {
    grid: "Grid-1",
    substation: "SUB-123",
    feeder: "FDR-5"
  },
  response: {
    automated: true,
    action: "Load shedding initiated",
    timestamp: ISODate("2024-01-30T16:05:00Z"),
    result: "Peak demand reduced"
  },
  acknowledged: true,
  acknowledgedBy: "system",
  acknowledgedAt: ISODate("2024-01-30T16:10:00Z")
}
```

**Key Design Decisions**:
- Comprehensive event types
- Duration tracking for outages
- Cost impact estimation
- Automated response capability
- Grid location tracking

### 6. Bills Collection
**Purpose**: Monthly billing and invoicing

```javascript
{
  billId: "BILL0000000001",
  buildingId: "BLD00000001",
  accountNumber: "ACC123456",
  billingPeriod: {
    start: ISODate("2024-01-01"),
    end: ISODate("2024-01-31"),
    days: 31
  },
  consumption: {
    totalKWh: 15000,               // Total consumption
    peakKWh: 6000,                 // During peak hours
    offPeakKWh: 7000,              // During off-peak
    shoulderKWh: 2000,             // During shoulder periods
    peakDemandKW: 275.5,           // Maximum demand
    averageDailyKWh: 483.9,
    powerFactor: 0.91
  },
  charges: {
    energyCharge: 1680.00,         // kWh charges
    demandCharge: 412.50,          // Peak demand charge
    fixedCharge: 50.00,            // Monthly fixed charge
    taxes: 150.00,
    adjustments: -25.00,           // Credits/adjustments
    credits: null,
    total: 2267.50
  },
  tariffApplied: {
    tariffId: "TAR1001",
    name: "Commercial Time-of-Use",
    rates: {
      peak: 0.18,
      offPeak: 0.09,
      flat: null
    }
  },
  comparison: {
    previousMonth: 2100.00,
    previousYear: 2050.00,
    percentChange: 7.9
  },
  status: "issued",                // draft|issued|sent|paid|overdue|disputed
  totalAmount: 2267.50,
  currency: "USD",
  dueDate: ISODate("2024-02-20"),
  issuedAt: ISODate("2024-02-03"),
  paidAt: null,
  paymentMethod: null
}
```

**Key Design Decisions**:
- Complete consumption breakdown
- Itemized charges
- Tariff tracking
- Historical comparison
- Payment status workflow

## Indexing Strategy

### Primary Indexes
```javascript
// Unique identifiers
db.buildings.createIndex({ buildingId: 1 }, { unique: true })
db.meters.createIndex({ meterId: 1 }, { unique: true })
db.tariffs.createIndex({ tariffId: 1 }, { unique: true })
db.events.createIndex({ eventId: 1 }, { unique: true })
db.bills.createIndex({ billId: 1 }, { unique: true })

// Time-series optimized
db.readings.createIndex({ "meta.meterId": 1, timestamp: -1 })
db.readings.createIndex({ "meta.buildingId": 1, timestamp: -1 })

// Operational queries
db.events.createIndex({ eventType: 1, severity: 1 })
db.bills.createIndex({ buildingId: 1, "billingPeriod.start": -1 })
```

## Data Flow Architecture

```
Smart Meters → Gateway → Readings (Time-Series)
                ↓
        Peak Detection → Events
                ↓
        Cost Calculation → Bills
                ↓
        Analytics & Reporting
```

## Key Design Patterns

### 1. Time-Series Optimization
- 15-minute interval readings
- Automatic compression and bucketing
- Metadata for efficient queries
- Granularity set to "minutes"

### 2. Demand Charge Calculation
```javascript
// Peak demand tracking
if (currentDemand > contractedMax) {
    demandCharge = (currentDemand - contractedMax) * penaltyRate
}
```

### 3. Time-of-Use Pricing
```javascript
// Determine pricing period
hour = timestamp.getHours()
if (hour >= 16 && hour <= 21) {
    rate = tariff.peak
} else if (hour >= 7 && hour <= 16) {
    rate = tariff.shoulder
} else {
    rate = tariff.offPeak
}
cost = consumption * rate
```

### 4. Power Quality Monitoring
- Voltage: 240V ±10%
- Frequency: 60Hz ±0.5Hz
- Power Factor: Target >0.90
- THD: Target <5%

## Energy Consumption Patterns

### Residential
- Morning peak: 6-9 AM (breakfast, showers)
- Evening peak: 6-10 PM (dinner, entertainment)
- Base load: 20-30% of peak
- Weekend: 10% higher than weekdays

### Commercial
- Business hours peak: 9 AM-5 PM
- Lunch dip: 12-1 PM
- After-hours: 20% of peak
- Weekend: 30% of weekday

### Industrial
- 24/7 operation: 70% base load
- Shift changes: Peak transitions
- Weekend: 80% of weekday
- Maintenance windows: Planned reductions

## Cost Calculation Logic

### Energy Charges
```javascript
// Time-of-use calculation
energyCost =
    (peakKWh * peakRate) +
    (offPeakKWh * offPeakRate) +
    (shoulderKWh * shoulderRate)
```

### Demand Charges
```javascript
// Monthly peak demand
demandCharge = peakDemandKW * demandRate
```

### Power Factor Penalty
```javascript
// Poor power factor penalty
if (powerFactor < 0.90) {
    penalty = totalCost * 0.05 * ((0.90 - powerFactor) / 0.10)
}
```

## Event Detection Rules

### Peak Demand Alert
```javascript
if (currentDemand > contractedMax * 0.9) {
    event = {
        type: "peak_demand",
        severity: currentDemand > contractedMax ? "critical" : "warning"
    }
}
```

### Voltage Quality
```javascript
if (voltage < 216 || voltage > 264) {  // ±10% of 240V
    event = {
        type: voltage < 216 ? "voltage_sag" : "voltage_spike",
        severity: "warning"
    }
}
```

## Analytics Patterns

### Daily Consumption Profile
```javascript
db.readings.aggregate([
    { $match: {
        timestamp: { $gte: startOfDay, $lt: endOfDay }
    }},
    { $group: {
        _id: { $hour: "$timestamp" },
        avgDemand: { $avg: "$kWDemand" },
        totalKWh: { $sum: "$kWhConsumed" }
    }},
    { $sort: { _id: 1 } }
])
```

### Cost Analysis by Period
```javascript
db.bills.aggregate([
    { $group: {
        _id: { $month: "$billingPeriod.start" },
        totalRevenue: { $sum: "$totalAmount" },
        avgBill: { $avg: "$totalAmount" },
        totalKWh: { $sum: "$consumption.totalKWh" }
    }}
])
```

## Performance Optimization

### Write Performance
- Batch inserts for readings (1000 documents)
- 15-minute intervals reduce volume
- Write concern w:1 for meter data
- Connection pooling for gateways

### Read Performance
- Time-series queries use metadata
- Covered queries for dashboards
- Aggregation pipelines with $match first
- Materialized views for billing

### Storage Efficiency
- Time-series compression (70% reduction)
- TTL indexes for old readings (optional)
- Archive old bills after 2 years
- Event retention for compliance

## Grid Stability Metrics

### Load Factor
```
Load Factor = Average Load / Peak Load
Target: >0.7 for efficiency
```

### Demand Factor
```
Demand Factor = Max Demand / Connected Load
Target: <0.8 for headroom
```

### Power Factor
```
Power Factor = Real Power / Apparent Power
Target: >0.90 for efficiency
```

## Future Enhancements

1. **Predictive Analytics**
   - Load forecasting with ML
   - Anomaly detection
   - Predictive maintenance

2. **Smart Grid Integration**
   - Demand response automation
   - Dynamic pricing
   - Grid balancing

3. **Renewable Integration**
   - Battery storage management
   - Solar forecasting
   - Net metering optimization

4. **Customer Portal**
   - Real-time consumption
   - Bill predictions
   - Energy saving tips