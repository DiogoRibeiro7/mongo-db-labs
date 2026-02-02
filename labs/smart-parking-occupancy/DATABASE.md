# Smart Parking Occupancy Database Design

## Overview

The Smart Parking Occupancy System database (`smartparking_db`) is designed for urban smart city infrastructure, tracking real-time parking space availability using IoT sensors (magnetometers, ultrasonic, infrared). The system monitors occupancy, detects violations, and provides analytics for parking management and revenue optimization.

## Key Features

- **Real-time Occupancy Tracking**: Binary occupancy status with confidence scores
- **Multi-Sensor Support**: Magnetometer, ultrasonic, infrared, camera sensors
- **Violation Detection**: Overstay, no payment, wrong spot type violations
- **Zone-Based Management**: Street, garage, lot, underground parking zones
- **Time-Series Analytics**: Occupancy patterns and peak hour analysis
- **Revenue Optimization**: Dynamic pricing and utilization metrics

## Collections Architecture

### 1. Zones Collection
**Purpose**: Define parking areas and their regulations

```javascript
{
  zoneId: "ZONE0001",              // Unique zone identifier
  name: "Downtown Central Plaza",
  type: "street",                  // street|garage|lot|underground|rooftop
  location: {
    type: "Polygon",
    coordinates: [[[...]]]         // GeoJSON polygon defining zone boundary
    address: "100-200 Market St",
    city: "San Francisco",
    district: "Financial District"
  },
  totalSpots: 45,
  reservedSpots: {
    disabled: 3,
    electric: 5,
    vip: 2,
    loading: 2
  },
  pricing: {
    currency: "USD",
    perHour: 4.50,
    perDay: 35.00,
    freeMinutes: 10,
    maxDailyCharge: 35.00,
    peakHourMultiplier: 1.5       // Rush hour pricing
  },
  regulations: {
    maxStayHours: 4,
    operatingHours: {
      start: "08:00",
      end: "22:00"
    },
    permitRequired: false,
    restrictions: ["No overnight parking", "Street cleaning Wed 6-8am"]
  },
  features: ["covered", "surveillance", "lighting", "ev_charging", "payment_app"]
}
```

**Key Design Decisions**:
- Polygon boundaries enable geofence-based queries
- Pricing structure supports dynamic and peak pricing
- Reserved spots tracked for compliance
- Features array for amenity filtering

### 2. Parking Spots Collection
**Purpose**: Individual parking space tracking

```javascript
{
  spotId: "SPOT00000001",          // Unique spot identifier
  zoneId: "ZONE0001",
  spotNumber: "A-101",             // Human-readable spot number
  type: "standard",                // standard|compact|disabled|electric|motorcycle|loading|vip
  status: "occupied",              // available|occupied|reserved|maintenance|violation
  location: {
    type: "Point",
    coordinates: [-122.4194, 37.7749],
    level: 0,                      // Floor/level for garages
    section: "A"
  },
  dimensions: {
    length: 5.0,
    width: 2.5,
    unit: "meters"
  },
  currentOccupant: {
    vehicleId: "VEH12345",
    licensePlate: "CA-123ABC",
    entryTime: ISODate("2024-01-30T14:30:00Z"),
    paymentMethod: "app",          // app|meter|permit|free
    paidUntil: ISODate("2024-01-30T16:30:00Z")
  },
  sensorId: "SEN00000001"          // Linked sensor
}
```

**Key Design Decisions**:
- Point location for precise spot positioning
- Current occupant embedded for fast queries
- Status field enables real-time availability
- Sensor linkage for IoT integration

### 3. Sensors Collection
**Purpose**: IoT sensor registry and configuration

```javascript
{
  sensorId: "SEN00000001",
  type: "magnetometer",            // magnetometer|ultrasonic|infrared|camera|radar
  model: "ParkSense MAG-3000",
  spotId: "SPOT00000001",
  zoneId: "ZONE0001",
  status: "active",                // active|inactive|faulty|maintenance|offline
  connectivity: {
    protocol: "LoRa",              // LoRa|NB-IoT|WiFi|Zigbee|4G
    gatewayId: "GW0001",
    signalStrength: -65,           // RSSI in dBm
    lastSeen: ISODate("2024-01-30T14:35:00Z")
  },
  calibration: {
    baseline: 150.0,               // Sensor-specific baseline
    threshold: 75.0,               // Detection threshold
    sensitivity: 7,                // 1-10 scale
    lastCalibrated: ISODate("2024-01-15T10:00:00Z")
  },
  batteryLevel: 85,                // Percentage
  firmware: {
    version: "2.3.1",
    lastUpdate: ISODate("2024-01-01T00:00:00Z")
  }
}
```

**Key Design Decisions**:
- Multiple sensor types for different environments
- LoRa protocol for low-power, long-range communication
- Calibration tracking for accuracy maintenance
- Battery monitoring for preventive maintenance

### 4. Occupancy Readings Collection (Time-Series)
**Purpose**: High-frequency sensor readings

```javascript
{
  timestamp: ISODate("2024-01-30T14:30:00Z"),
  meta: {                          // Time-series metadata
    spotId: "SPOT00000001",
    sensorId: "SEN00000001",
    zoneId: "ZONE0001"
  },
  occupied: true,                  // Binary occupancy status
  confidence: 0.95,                // 0-1 confidence score
  status: "occupied",              // Detailed status

  // Sensor-specific data
  magneticField: 235.5,            // For magnetometer
  fieldStrength: 85.5,
  distance: 120,                   // For ultrasonic (cm)
  echoTime: 698.5,                 // Microseconds
  irReflection: 0.82,              // For infrared

  batteryLevel: 85,
  signalStrength: -65,
  processingTime: 23.5             // Milliseconds
}
```

**Key Design Decisions**:
- Time-series collection for compression and performance
- Confidence scores for reliability assessment
- Sensor-specific fields for diagnostics
- Processing time for latency monitoring

### 5. Events Collection
**Purpose**: Parking events and state changes

```javascript
{
  eventId: "EVT0000000001",
  eventType: "occupancy_change",   // occupancy_change|overstay_warning|overstay_violation|
                                   // payment_expired|sensor_offline|illegal_parking
  spotId: "SPOT00000001",
  zoneId: "ZONE0001",
  sensorId: "SEN00000001",
  timestamp: ISODate("2024-01-30T14:30:00Z"),
  endTime: ISODate("2024-01-30T14:35:00Z"),  // For duration events
  details: {
    previousStatus: "available",
    newStatus: "occupied",
    confidence: 0.95,
    vehicleId: "VEH12345",
    duration: 180                  // Minutes for completed stays
  },
  severity: "info",                // info|warning|critical
  acknowledged: false
}
```

**Key Design Decisions**:
- Comprehensive event types for operations
- Details object for event-specific data
- Severity levels for alert prioritization
- Acknowledgment tracking for workflow

### 6. Violations Collection
**Purpose**: Parking violations and enforcement

```javascript
{
  violationId: "VIO0000000001",
  type: "overstay",                // overstay|no_payment|invalid_permit|wrong_spot_type|
                                   // outside_hours|double_parking|blocked_access
  spotId: "SPOT00000001",
  zoneId: "ZONE0001",
  vehicle: {
    licensePlate: "CA-123ABC",
    make: "Toyota",
    model: "Camry",
    color: "Silver",
    imageUrl: "/images/violations/0000000001.jpg"
  },
  timestamp: ISODate("2024-01-30T15:00:00Z"),
  detectedBy: "sensor",            // sensor|camera|officer|user_report
  fine: {
    amount: 35.00,
    currency: "USD",
    dueDate: ISODate("2024-02-29T23:59:59Z")
  },
  status: "active",                 // active|paid|disputed|cancelled|escalated
  evidence: [{
    type: "sensor_log",            // photo|sensor_log|video
    url: "/evidence/sensor/0000000001",
    timestamp: ISODate("2024-01-30T15:00:00Z")
  }],
  officer: {
    badgeNumber: "P1234",
    name: "Officer Smith"
  },
  resolution: {
    status: "paid",
    date: ISODate("2024-02-15T10:00:00Z"),
    amount: 35.00,
    notes: "Paid online"
  }
}
```

**Key Design Decisions**:
- Vehicle details for enforcement
- Evidence array for dispute resolution
- Fine structure with due dates
- Resolution tracking for closure

## Indexing Strategy

### Primary Indexes
```javascript
// Unique identifiers
db.zones.createIndex({ zoneId: 1 }, { unique: true })
db.parking_spots.createIndex({ spotId: 1 }, { unique: true })
db.sensors.createIndex({ sensorId: 1 }, { unique: true })
db.events.createIndex({ eventId: 1 }, { unique: true })
db.violations.createIndex({ violationId: 1 }, { unique: true })

// Geospatial indexes
db.zones.createIndex({ "location.coordinates": "2dsphere" })
db.parking_spots.createIndex({ "location.coordinates": "2dsphere" })

// Time-series optimized
db.occupancy_readings.createIndex({ "meta.spotId": 1, timestamp: -1 })
db.occupancy_readings.createIndex({ "meta.zoneId": 1, timestamp: -1 })

// Operational queries
db.parking_spots.createIndex({ zoneId: 1, status: 1 })
db.violations.createIndex({ "vehicle.licensePlate": 1 })
db.events.createIndex({ eventType: 1, timestamp: -1 })
```

## Data Flow Architecture

```
IoT Sensors → LoRa Gateway → Occupancy Readings
                ↓
        Event Detection
                ↓
        Status Updates → Parking Spots
                ↓
        Violation Detection → Violations
                ↓
        Analytics & Reporting
```

## Key Design Patterns

### 1. Binary Occupancy with Confidence
Each reading provides:
- **Binary Status**: Occupied (true/false)
- **Confidence Score**: 0-1 probability
- **Sensor Data**: Raw readings for validation

This allows for:
- Quick availability checks
- Reliability assessment
- False positive/negative detection

### 2. Zone-Based Aggregation
Hierarchical structure enables:
- Zone-level occupancy rates
- District-wide analytics
- City-level dashboards
- Revenue aggregation by area

### 3. Event-Driven Architecture
State changes trigger events:
```
Occupancy Change → Event → Status Update → Possible Violation
```

### 4. Sensor Fusion
Multiple sensor types provide redundancy:
- **Magnetometer**: Detects metal (vehicles)
- **Ultrasonic**: Measures distance
- **Infrared**: Detects presence
- **Camera**: Visual confirmation

## Occupancy Detection Logic

### Magnetometer Sensors
```javascript
// Detect vehicle presence by magnetic field distortion
if (magneticField - baseline > threshold) {
    occupied = true;
    confidence = min(1.0, (magneticField - baseline) / (threshold * 2));
}
```

### Ultrasonic Sensors
```javascript
// Detect by distance measurement
if (distance < emptySpaceDistance * 0.6) {
    occupied = true;
    confidence = 1.0 - (distance / emptySpaceDistance);
}
```

### Confidence Scoring
- **0.95-1.00**: Very high confidence
- **0.85-0.95**: High confidence
- **0.70-0.85**: Medium confidence
- **Below 0.70**: Low confidence (may require verification)

## Violation Detection Rules

### Overstay Detection
```javascript
if (currentTime > paidUntil + gracePeriod) {
    violation = {
        type: "overstay",
        overstayMinutes: (currentTime - paidUntil) / 60000
    }
}
```

### Wrong Spot Type
```javascript
if (vehicleType !== spotType && !hasPermit) {
    violation = {
        type: "wrong_spot_type",
        details: `${vehicleType} in ${spotType} spot`
    }
}
```

## Analytics Patterns

### Hourly Occupancy Rate
```javascript
db.occupancy_readings.aggregate([
    { $match: { timestamp: { $gte: startTime, $lt: endTime } } },
    { $group: {
        _id: {
            hour: { $hour: "$timestamp" },
            zoneId: "$meta.zoneId"
        },
        occupancyRate: { $avg: { $cond: ["$occupied", 1, 0] } }
    }}
])
```

### Zone Turnover Rate
```javascript
db.events.aggregate([
    { $match: {
        eventType: "occupancy_change",
        "details.newStatus": "occupied"
    }},
    { $group: {
        _id: "$zoneId",
        turnoverCount: { $sum: 1 }
    }}
])
```

### Revenue Analysis
```javascript
db.violations.aggregate([
    { $match: { status: "paid" } },
    { $group: {
        _id: "$zoneId",
        totalRevenue: { $sum: "$fine.amount" },
        avgFine: { $avg: "$fine.amount" }
    }}
])
```

## Performance Optimization

### Write Performance
- Batch inserts for readings (1000 documents)
- Asynchronous event processing
- Write concern w:1 for sensor data
- Connection pooling for gateways

### Read Performance
- Time-series queries use metadata filtering
- Covered queries for dashboards
- Aggregation pipelines with early $match
- Materialized views for reports

### Storage Efficiency
- Time-series compression (60-70% reduction)
- TTL indexes for old readings (optional)
- Sparse indexes for optional fields
- Archive strategy for violations

## Security Considerations

### Data Validation
- JSON Schema validation on all collections
- Pattern matching for IDs
- Enum constraints for types/statuses
- Range validation for coordinates

### Privacy Protection
- License plates can be hashed
- Personal data in separate collection
- Role-based access control
- Audit logging for violations

## Scaling Strategy

### Horizontal Scaling
- Shard by zoneId for geographic distribution
- Time-series sharding by timestamp
- Read replicas for analytics
- Edge computing at gateways

### Vertical Scaling
- Dedicated time-series nodes
- SSD storage for recent data
- Memory for hot indexes
- Compression for archives

## Common Use Cases

### 1. Find Available Spots Near Location
```javascript
db.parking_spots.find({
    status: "available",
    "location.coordinates": {
        $near: {
            $geometry: { type: "Point", coordinates: [lon, lat] },
            $maxDistance: 500
        }
    }
})
```

### 2. Peak Hour Analysis
```javascript
db.occupancy_readings.aggregate([
    { $match: {
        timestamp: { $gte: todayStart, $lt: todayEnd }
    }},
    { $group: {
        _id: { $hour: "$timestamp" },
        avgOccupancy: { $avg: { $cond: ["$occupied", 1, 0] } }
    }},
    { $sort: { avgOccupancy: -1 } }
])
```

### 3. Violation Hot Spots
```javascript
db.violations.aggregate([
    { $group: {
        _id: "$spotId",
        violationCount: { $sum: 1 },
        totalFines: { $sum: "$fine.amount" }
    }},
    { $sort: { violationCount: -1 } },
    { $limit: 10 }
])
```

## Future Enhancements

1. **Predictive Occupancy**
   - ML models for availability prediction
   - Demand forecasting by zone
   - Optimal pricing recommendations

2. **Enhanced Detection**
   - Computer vision for vehicle type
   - License plate recognition
   - Multi-sensor fusion algorithms

3. **Smart Features**
   - Reservation system integration
   - Dynamic pricing based on demand
   - EV charger availability tracking
   - Navigation app integration

4. **Operational Improvements**
   - Predictive maintenance for sensors
   - Automatic violation appeals
   - Real-time enforcement routing