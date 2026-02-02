# Database Design: Agricultural Pest & Disease Risk Scoring System

## Overview

The `agrimonitor_db` database implements a comprehensive agricultural monitoring system for pest and disease risk assessment across multiple farms. It tracks environmental conditions, pest populations, and calculates risk scores to provide actionable management recommendations.

## Database Structure

```
agrimonitor_db/
├── farms (Standard Collection)
├── fields (Standard Collection)
├── sensors (Standard Collection)
├── measurements (Time-Series Collection)
├── risk_assessments (Standard Collection)
└── events (Standard Collection with TTL)
```

## Collections

### 1. farms Collection

**Purpose**: Stores information about agricultural operations and their management practices.

**Schema**:
```javascript
{
  farmId: String (unique),           // "FARM00000001"
  name: String (required),           // "Green Valley Vineyard"
  location: {
    type: "Point",                   // GeoJSON point
    coordinates: [lon, lat],         // [-120.5, 35.7]
    address: String,
    region: String,                  // "California Central Valley"
    climate: String                  // "Mediterranean"
  },
  owner: {
    name: String (required),
    contactEmail: String (email),    // Valid email format
    contactPhone: String
  },
  area: {
    total: Number (positive),        // 250
    cultivated: Number (positive),   // 200
    unit: String                     // "hectares" or "acres"
  },
  management: {
    pestManagement: String (enum),   // "IPM", "organic", "conventional"
    irrigationType: String,          // "drip", "sprinkler", "flood"
    certification: [String]          // ["USDA Organic", "GlobalGAP"]
  },
  certifications: {
    organic: Boolean,
    globalGAP: Boolean,
    rainforest: Boolean,
    fairtrade: Boolean
  },
  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `farmId`: Unique index
- `location`: 2dsphere index for geospatial queries
- `owner.contactEmail`: Standard index
- `management.pestManagement`: Standard index

**Validation Rules**:
- Coordinates must be valid (lon: -180 to 180, lat: -90 to 90)
- Email must contain @ and domain
- Area values must be positive
- Pest management must be from allowed enum

### 2. fields Collection

**Purpose**: Represents individual cultivation areas within farms with specific crops and conditions.

**Schema**:
```javascript
{
  fieldId: String (unique),          // "FLD00000001"
  farmId: String (required),         // Reference to farm
  name: String (required),           // "North Block A"
  area: Number (positive),           // 5.5 hectares
  crop: {
    type: String (required),         // "grape", "tomato", "corn"
    variety: String,                 // "Cabernet Sauvignon"
    plantingDate: Date,
    expectedHarvest: Date,
    growthStage: String (enum)       // "seedling", "vegetative", "flowering", "fruiting", "harvest"
  },
  soil: {
    type: String,                    // "loamy", "clay", "sandy"
    pH: Number (0-14),              // 6.5
    organicMatter: Number,           // Percentage
    lastTested: Date
  },
  location: {
    type: "Polygon",                 // GeoJSON polygon
    coordinates: [[[lon,lat],...]]   // Field boundaries
  },
  irrigation: {
    type: String,                    // "drip", "sprinkler"
    schedule: String                 // "daily", "weekly"
  },
  riskHistory: {
    averageRisk: Number (0-100),
    highestRisk: Number (0-100),
    lastHighRisk: Date,
    commonDiseases: [String],
    commonPests: [String]
  },
  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `fieldId`: Unique index
- `farmId`: Standard index
- `crop.type, crop.growthStage`: Compound index
- `location`: 2dsphere index
- `riskHistory.averageRisk`: Standard index

**Validation Rules**:
- Growth stage must be from allowed enum
- Soil pH must be 0-14
- Area must be positive
- Polygon coordinates must form valid closed shape

### 3. sensors Collection

**Purpose**: Tracks monitoring devices deployed across fields.

**Schema**:
```javascript
{
  sensorId: String (unique),         // "SNS00000001"
  fieldId: String (required),        // Reference to field
  sensorType: String (enum),         // "weather_station", "leaf_wetness", "pest_trap", "soil_moisture"
  manufacturer: String,               // "Davis Instruments"
  model: String,                      // "Vantage Pro2"
  installDate: Date,
  lastMaintenance: Date,
  nextMaintenance: Date,
  status: String (enum),              // "active", "maintenance", "inactive"
  location: {
    type: "Point",
    coordinates: [lon, lat],
    elevation: Number,                // Meters above sea level
    placement: String                 // "canopy", "ground", "2m_pole"
  },
  configuration: {
    samplingInterval: Number,         // Minutes between readings
    unit: String,                     // "minutes", "hours"
    parameters: [String]              // ["temperature", "humidity", "rainfall"]
  },
  calibration: {
    lastCalibrated: Date,
    nextCalibration: Date,
    offset: Object                    // Calibration adjustments
  },
  connectivity: {
    type: String,                     // "wifi", "cellular", "LoRaWAN"
    signalStrength: Number,
    lastContact: Date
  },
  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `sensorId`: Unique index
- `fieldId, sensorType`: Compound index
- `status`: Standard index
- `location`: 2dsphere index
- `lastContact`: Standard index (for monitoring)

**Validation Rules**:
- Sensor type must be from allowed enum
- Status must be from allowed enum
- Sampling interval must be positive
- Coordinates must be valid

### 4. measurements Collection (Time-Series)

**Purpose**: Stores sensor readings with time-series optimization.

**Time-Series Configuration**:
```javascript
{
  timeseries: {
    timeField: "timestamp",
    metaField: "meta",
    granularity: "minutes"
  },
  expireAfterSeconds: 31536000  // 1 year retention
}
```

**Schema**:
```javascript
{
  timestamp: Date (required),         // Reading time
  meta: {                            // Time-series metadata
    sensorId: String,
    fieldId: String,
    sensorType: String
  },
  // Data varies by sensor type:

  // Weather Station
  data: {
    temperature: Number (-50 to 60),  // Celsius
    humidity: Number (0-100),         // Percentage
    rainfall: Number (0-500),         // mm
    windSpeed: Number (0-200),        // km/h
    windDirection: Number (0-360),    // Degrees
    pressure: Number (900-1100),      // mbar
    solarRadiation: Number            // W/m²
  },

  // Leaf Wetness Sensor
  data: {
    leafWetnessHours: Number (0-24),  // Hours wet
    surfaceTemperature: Number,       // Celsius
    humidity: Number (0-100),         // Percentage
    dewPoint: Number                  // Celsius
  },

  // Pest Trap
  data: {
    trapCount: Number (0-1000),       // Insects counted
    pestType: String,                 // "aphids", "whitefly", etc.
    temperature: Number,              // Ambient temperature
    imageUrl: String                  // Photo evidence
  },

  // Soil Moisture
  data: {
    moisturePercent: Number (0-100),  // Volumetric water content
    soilTemperature: Number,          // Celsius
    electricalConductivity: Number,   // dS/m
    depth: Number                     // Sensor depth in cm
  },

  quality: {
    status: String,                   // "valid", "suspect", "invalid"
    confidence: Number (0-1),         // Data quality score
    issues: [String]                  // ["sensor_drift", "out_of_range"]
  }
}
```

**Indexes**:
- `timestamp, meta.fieldId`: Compound index (automatic for time-series)
- `meta.sensorType, timestamp`: Compound index
- `data.trapCount`: Partial index (where exists)

**Validation Rules**:
- Temperature must be -50 to 60°C
- Humidity must be 0-100%
- Rainfall must be non-negative
- Trap count must be 0-1000
- All percentages must be 0-100

### 5. risk_assessments Collection

**Purpose**: Stores calculated risk scores with detailed factor analysis.

**Schema**:
```javascript
{
  assessmentId: String (unique),      // "RISK00000001"
  fieldId: String (required),         // Reference to field
  assessmentTime: Date (required),
  riskScore: Number (0-100),         // Overall risk score
  category: String (enum),           // "LOW", "MODERATE", "HIGH", "CRITICAL"

  factors: {
    leafWetness: {
      value: Number,                  // Hours of wetness
      weight: Number (0-1),           // 0.30 (30% weight)
      contribution: Number (0-100),   // Contribution to risk
      threshold: Number               // Critical threshold
    },
    temperature: {
      value: Number,                  // Celsius
      weight: Number (0-1),           // 0.20 (20% weight)
      contribution: Number (0-100),
      optimal: Boolean                // In pathogen optimal range
    },
    humidity: {
      value: Number,                  // Percentage
      weight: Number (0-1),           // 0.20 (20% weight)
      contribution: Number (0-100),
      duration: Number                // Hours above threshold
    },
    rainfall: {
      value: Number,                  // mm in period
      weight: Number (0-1),           // 0.15 (15% weight)
      contribution: Number (0-100),
      consecutive: Number             // Days with rain
    },
    trapCount: {
      value: Number,                  // Average count
      weight: Number (0-1),           // 0.15 (15% weight)
      contribution: Number (0-100),
      trend: String                  // "increasing", "stable", "decreasing"
    }
  },

  diseases: [String],                 // ["powdery_mildew", "late_blight"]
  pests: [String],                   // ["aphids", "whitefly"]

  explanation: String,                // Human-readable risk explanation
  recommendation: String,             // Action recommendation
  products: [{
    type: String,                    // "fungicide", "insecticide"
    name: String,                    // "Copper Sulfate"
    activeIngredient: String,
    dosage: String,
    timing: String                   // "Apply within 24 hours"
  }],

  confidence: Number (0-1),          // Model confidence
  modelVersion: String,              // "v1.2.0"

  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `assessmentId`: Unique index
- `fieldId, assessmentTime`: Compound index
- `riskScore`: Standard index
- `category`: Standard index
- `assessmentTime`: Standard index (descending)

**Validation Rules**:
- Risk score must be 0-100
- Category must be from allowed enum
- Factor weights must sum to 1.0
- All contributions must be 0-100
- Confidence must be 0-1

### 6. events Collection

**Purpose**: Tracks significant occurrences requiring attention or action.

**Schema**:
```javascript
{
  eventId: String (unique),          // "EVT00000001"
  fieldId: String (required),        // Reference to field
  eventType: String (enum),          // "SPRAY_RECOMMENDATION", "RISK_ALERT", "PEST_OUTBREAK", "DISEASE_DETECTION"
  severity: String (enum),           // "low", "medium", "high", "critical"
  timestamp: Date (required),

  description: String,                // Detailed event description

  metadata: {
    riskScore: Number,               // Associated risk score
    triggerThreshold: Number,        // Threshold that triggered event
    measurements: [ObjectId],        // Related measurement IDs
    assessmentId: String,           // Related risk assessment

    // For spray recommendations
    product: String,
    activeIngredient: String,
    applicationRate: String,
    rei: Number,                    // Re-entry interval (hours)
    phi: Number,                    // Pre-harvest interval (days)

    // For pest/disease events
    species: String,                // Pest or disease species
    infestationLevel: String,       // "low", "moderate", "severe"
    affectedArea: Number,           // Hectares affected

    // For weather events
    weatherCondition: String,
    duration: Number,
    intensity: String
  },

  actionTaken: {
    status: String,                 // "pending", "in_progress", "completed", "dismissed"
    action: String,                 // What was done
    timestamp: Date,
    performedBy: String,
    result: String,
    cost: Number
  },

  acknowledged: Boolean,
  acknowledgedBy: String,
  acknowledgedAt: Date,

  notificationsSent: [{
    channel: String,                // "email", "sms", "app"
    recipient: String,
    sentAt: Date,
    status: String                  // "sent", "delivered", "failed"
  }],

  expiresAt: Date,                  // TTL for event cleanup
  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `eventId`: Unique index
- `fieldId, timestamp`: Compound index
- `eventType, severity`: Compound index
- `timestamp`: Standard index (descending)
- `expiresAt`: TTL index (90 days)
- `acknowledged, severity`: Compound index

**Validation Rules**:
- Event type must be from allowed enum
- Severity must be from allowed enum
- Timestamp must not be future
- REI and PHI must be positive if present

## Aggregation Pipelines

### 1. Risk Trend Analysis
```javascript
[
  { $match: { fieldId: "FLD00000001" } },
  { $group: {
    _id: { $dateToString: { format: "%Y-%m-%d", date: "$assessmentTime" } },
    avgRisk: { $avg: "$riskScore" },
    maxRisk: { $max: "$riskScore" }
  }},
  { $sort: { _id: 1 } }
]
```

### 2. Rainfall Correlation
```javascript
[
  { $lookup: {
    from: "measurements",
    localField: "fieldId",
    foreignField: "meta.fieldId",
    as: "weather"
  }},
  { $unwind: "$weather" },
  { $group: {
    _id: "$fieldId",
    correlation: { /* correlation calculation */ }
  }}
]
```

### 3. Top Risk Plots
```javascript
[
  { $sort: { riskScore: -1 } },
  { $limit: 10 },
  { $lookup: {
    from: "fields",
    localField: "fieldId",
    foreignField: "fieldId",
    as: "field"
  }}
]
```

## Performance Optimization

### 1. Time-Series Benefits
- 70% storage reduction for measurements
- Automatic data compression
- Optimized for time-based queries
- Built-in downsampling support

### 2. Index Strategy
- Cover queries with compound indexes
- Use partial indexes for sparse data
- 2dsphere indexes for location queries
- TTL indexes for automatic cleanup

### 3. Query Optimization
- Use $match early in pipelines
- Leverage covered queries
- Batch inserts for bulk data
- Use projections to limit data transfer

## Data Retention Policy

| Collection | Retention Period | Method |
|------------|-----------------|--------|
| measurements | 1 year | TTL index |
| risk_assessments | 2 years | Manual archival |
| events | 90 days | TTL index |
| farms | Permanent | - |
| fields | Permanent | - |
| sensors | Permanent | - |

## Security Considerations

1. **Field-Level Encryption**: Sensitive farm owner data
2. **Role-Based Access**: Different roles for farmers, consultants, admins
3. **Audit Logging**: Track all data modifications
4. **API Rate Limiting**: Prevent abuse
5. **Data Validation**: Strict schema validation

## Backup Strategy

1. **Daily Backups**: Full database backup
2. **Continuous Replication**: Real-time replica set
3. **Point-in-Time Recovery**: Oplog retention for 24 hours
4. **Geographic Distribution**: Replicas in different regions
5. **Backup Testing**: Monthly restoration tests

## Monitoring Metrics

1. **System Health**
   - Database connections
   - Query performance
   - Storage usage
   - Index usage

2. **Business Metrics**
   - Active sensors per field
   - Risk assessments per day
   - Event response time
   - Data quality scores

3. **Alerts**
   - High risk scores
   - Sensor failures
   - Data gaps
   - System errors

## Future Enhancements

1. **Machine Learning Integration**
   - Predictive risk models
   - Pattern recognition
   - Anomaly detection

2. **Weather API Integration**
   - Forecast data
   - Historical weather
   - Climate modeling

3. **Mobile App Support**
   - Real-time notifications
   - Photo uploads
   - Offline capability

4. **Blockchain Integration**
   - Certification tracking
   - Supply chain transparency
   - Smart contracts

5. **Advanced Analytics**
   - Yield prediction
   - Cost optimization
   - Resource efficiency