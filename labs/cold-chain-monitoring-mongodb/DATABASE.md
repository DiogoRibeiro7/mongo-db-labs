# Cold Chain Monitoring Database Design

## Overview

The Cold Chain Monitoring System database (`coldchain_db`) is designed to track temperature-controlled logistics for pharmaceuticals, food, and other temperature-sensitive products. The system monitors assets (refrigerators, freezers, trucks, containers) through IoT sensors, ensuring compliance with temperature requirements throughout the supply chain.

## Key Features

- **Time-Series Data**: Optimized for high-frequency sensor readings
- **Adaptive Sampling**: Dynamic measurement frequency based on conditions
- **Real-time Monitoring**: Event-driven alerts for temperature excursions
- **Geospatial Tracking**: Location monitoring for mobile assets
- **Compliance Reporting**: Audit trails and temperature history
- **Schema Validation**: Strict data integrity enforcement

## Collections Architecture

### 1. Assets Collection
**Purpose**: Master data for all monitored equipment

```javascript
{
  assetId: "FRG000001",           // Unique identifier with type prefix
  assetType: "refrigerator",      // refrigerator|freezer|truck|container|warehouse
  name: "Pharma Fridge Unit 1",
  status: "active",               // active|inactive|maintenance|in_transit|alarm
  location: {
    type: "Point",
    coordinates: [-73.935242, 40.730610],
    address: "123 Medical Center Dr"
  },
  temperatureRange: {
    min: 2.0,                    // Minimum allowed temperature
    max: 8.0,                    // Maximum allowed temperature
    optimal: 5.0,                // Target temperature
    unit: "C"
  },
  capacity: {
    volume: 500,
    unit: "L",
    currentLoad: 75              // Percentage
  }
}
```

**Key Design Decisions**:
- Asset IDs use prefixes for quick type identification
- GeoJSON format for location enables spatial queries
- Temperature ranges embedded for fast validation
- Status field enables operational queries

### 2. Sensors Collection
**Purpose**: IoT device registry and configuration

```javascript
{
  sensorId: "SEN00000001",
  assetId: "FRG000001",
  sensorType: "temperature",     // temperature|humidity|door|gps|shock|power
  model: "TempTrack Pro 2000",
  status: "active",               // active|inactive|faulty|calibrating
  position: "top_shelf",
  calibration: {
    offset: 0.2,
    lastCalibrated: ISODate("2024-01-15"),
    nextCalibration: ISODate("2024-07-15")
  },
  batteryLevel: 85
}
```

**Key Design Decisions**:
- One-to-many relationship with assets
- Calibration data tracked for accuracy
- Battery monitoring for maintenance
- Position field for multi-zone monitoring

### 3. Measurements Collection (Time-Series)
**Purpose**: High-frequency telemetry data storage

```javascript
{
  timestamp: ISODate("2024-01-30T14:30:00Z"),
  meta: {                        // Time-series metadata field
    assetId: "FRG000001",
    sensorId: "SEN00000001",
    routeId: "RT00000001"        // Optional for transport
  },
  temperature: 5.2,
  humidity: 45.5,
  doorOpen: false,
  location: {                    // For mobile assets
    type: "Point",
    coordinates: [-73.935242, 40.730610]
  },
  batteryLevel: 85,
  signalStrength: -65,           // RSSI in dBm
  samplingMode: "normal"         // normal|rapid|adaptive|alarm
}
```

**Key Design Decisions**:
- MongoDB time-series collection for optimal storage
- Metadata field groups related measurements
- Adaptive sampling mode tracked per reading
- Sparse fields (location only for mobile assets)

### 4. Events Collection
**Purpose**: Operational events and incidents

```javascript
{
  eventId: "EVT0000000001",
  assetId: "FRG000001",
  eventType: "door_open",        // door_open|power_failure|temperature_excursion
  timestamp: ISODate("2024-01-30T14:30:00Z"),
  endTime: ISODate("2024-01-30T14:35:00Z"),
  severity: "warning",            // info|warning|critical
  details: {
    duration_seconds: 300,
    temperature_at_open: 5.2,
    temperature_at_close: 6.8
  },
  acknowledged: false
}
```

**Key Design Decisions**:
- Separate from measurements for event-driven queries
- Flexible details object for event-specific data
- Acknowledgment tracking for operations
- Duration tracking via endTime field

### 5. Routes Collection
**Purpose**: Transport tracking and planning

```javascript
{
  routeId: "RT00000001",
  assetId: "TRK000001",
  status: "in_progress",          // planned|in_progress|completed|cancelled|delayed
  origin: {
    name: "Distribution Center A",
    coordinates: [-73.935242, 40.730610]
  },
  destination: {
    name: "Pharmacy B",
    coordinates: [-74.006020, 40.712776]
  },
  waypoints: [{
    name: "Transfer Point 1",
    coordinates: [-73.950000, 40.720000],
    arrivalTime: ISODate("2024-01-30T15:00:00Z")
  }],
  cargo: {
    description: "Insulin shipment",
    quantity: 100,
    value: 50000,
    temperatureRequirement: {
      min: 2.0,
      max: 8.0
    }
  },
  startTime: ISODate("2024-01-30T14:00:00Z"),
  expectedEndTime: ISODate("2024-01-30T18:00:00Z")
}
```

**Key Design Decisions**:
- Links mobile assets to shipments
- Waypoint tracking for multi-stop routes
- Cargo-specific temperature requirements
- Status field for operational visibility

### 6. Alerts Collection
**Purpose**: Real-time alerting and escalation

```javascript
{
  alertId: "ALT0000000001",
  assetId: "FRG000001",
  alertType: "temperature_high",   // temperature_high|humidity_low|door_open_too_long
  severity: "high",                // low|medium|high|critical
  status: "active",                // active|acknowledged|resolved|escalated
  threshold: {
    metric: "temperature",
    operator: ">",
    value: 8.0,
    duration: 300                  // Seconds before triggering
  },
  actualValue: 9.5,
  message: "High temperature alert: 9.5°C exceeds maximum 8.0°C",
  triggeredAt: ISODate("2024-01-30T14:30:00Z"),
  assignedTo: "john.doe@company.com",
  notes: [{
    timestamp: ISODate("2024-01-30T14:35:00Z"),
    user: "jane.smith",
    note: "Technician dispatched"
  }]
}
```

**Key Design Decisions**:
- Threshold configuration for rule-based alerting
- Escalation workflow via status field
- Assignment tracking for accountability
- Notes array for incident management

## Indexing Strategy

### Primary Indexes
```javascript
// Unique identifiers
db.assets.createIndex({ assetId: 1 }, { unique: true })
db.sensors.createIndex({ sensorId: 1 }, { unique: true })
db.events.createIndex({ eventId: 1 }, { unique: true })
db.routes.createIndex({ routeId: 1 }, { unique: true })
db.alerts.createIndex({ alertId: 1 }, { unique: true })

// Time-series optimized
db.measurements.createIndex({ "meta.assetId": 1, timestamp: -1 })
db.measurements.createIndex({ "meta.sensorId": 1, timestamp: -1 })

// Geospatial
db.assets.createIndex({ "location.coordinates": "2dsphere" })

// Operational queries
db.alerts.createIndex({ assetId: 1, status: 1, triggeredAt: -1 })
db.events.createIndex({ assetId: 1, timestamp: -1 })
```

### Query Optimization
- Compound indexes for common query patterns
- Time-descending indexes for recent data access
- Partial indexes for active records only
- TTL indexes for data retention (optional)

## Data Flow Architecture

```
Sensors → Measurements (Time-Series)
    ↓
Adaptive Sampling Engine
    ↓
Events Generation (Incidents)
    ↓
Alert Engine (Thresholds)
    ↓
Notifications & Escalation
```

## Key Design Patterns

### 1. Adaptive Sampling
The system dynamically adjusts measurement frequency based on conditions:
- **Normal Mode**: 5-minute intervals when stable
- **Adaptive Mode**: 2-minute intervals when approaching limits
- **Rapid Mode**: 1-minute intervals when exceeding thresholds
- **Alarm Mode**: 30-second intervals during critical events

### 2. Time-Series Optimization
- MongoDB time-series collections for measurements
- Automatic bucketing and compression
- Metadata field for efficient queries
- Granularity set to "seconds" for precision

### 3. Event Sourcing
- All state changes recorded as events
- Immutable event log for compliance
- Event replay capability for auditing
- Correlation between events and measurements

### 4. Hierarchical Monitoring
```
Asset (Container)
  ├── Primary Sensor (Main zone)
  ├── Secondary Sensor (Backup)
  └── Door Sensor (Access monitoring)
```

## Compliance Features

### Temperature Excursion Tracking
- Automatic detection when limits exceeded
- Duration and severity recorded
- Maximum deviation captured
- Recovery time tracked

### Audit Trail
- All events immutable once created
- User actions tracked with timestamps
- Alert acknowledgments recorded
- Compliance reports via aggregation

### Data Retention
- Measurements: 2 years (configurable)
- Events: 5 years (regulatory requirement)
- Alerts: 3 years (incident history)
- Routes: 1 year (operational data)

## Performance Considerations

### Write Performance
- Batch inserts for measurements (1000 documents)
- Asynchronous event generation
- Write concern tuning for sensor data
- Connection pooling for high throughput

### Read Performance
- Time-series optimized queries
- Covered queries for dashboards
- Aggregation pipelines for analytics
- Caching for reference data

### Storage Efficiency
- Time-series compression (70-80% reduction)
- Sparse indexes for optional fields
- Document validation at database level
- Archival strategy for old data

## Security Model

### Data Validation
- JSON Schema validation on all collections
- Pattern matching for IDs
- Range validation for measurements
- Enum constraints for status fields

### Access Control
- Read-only access for monitoring
- Write access for sensor gateways
- Admin access for configuration
- Audit logging for all changes

## Scaling Strategy

### Horizontal Scaling
- Sharding by asset ID for measurements
- Read replicas for analytics
- Geographic distribution for global ops
- Time-based partitioning option

### Vertical Scaling
- Dedicated time-series nodes
- SSD storage for hot data
- Memory optimization for indexes
- Compression for cold storage

## Common Queries

### Real-time Monitoring
```javascript
// Current temperature for all assets
db.measurements.aggregate([
  { $sort: { timestamp: -1 } },
  { $group: {
    _id: "$meta.assetId",
    lastTemp: { $first: "$temperature" },
    lastTime: { $first: "$timestamp" }
  }}
])
```

### Compliance Reporting
```javascript
// Temperature excursions in last 24 hours
db.events.find({
  eventType: "temperature_excursion",
  timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
})
```

### Route Analysis
```javascript
// Average temperature during transport
db.measurements.aggregate([
  { $match: { "meta.routeId": "RT00000001" } },
  { $group: {
    _id: null,
    avgTemp: { $avg: "$temperature" },
    maxTemp: { $max: "$temperature" },
    minTemp: { $min: "$temperature" }
  }}
])
```

## Future Enhancements

1. **Predictive Maintenance**
   - ML models for failure prediction
   - Sensor degradation detection
   - Optimal calibration scheduling

2. **Advanced Analytics**
   - Temperature stability metrics
   - Door open pattern analysis
   - Route optimization algorithms

3. **Integration Points**
   - ERP system connectivity
   - Blockchain for compliance
   - Real-time notification services

4. **Enhanced Monitoring**
   - Multi-zone temperature mapping
   - Vibration and shock detection
   - Light exposure tracking