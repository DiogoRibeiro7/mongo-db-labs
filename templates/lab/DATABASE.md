# Data Dictionary for {{LAB_NAME}}

## Database: `{{DATABASE_NAME}}`

This document provides complete documentation for all collections, fields, and data types used in the {{LAB_NAME}} lab.

---

## Collections Overview

| Collection | Type | Description | Document Count (Typical) |
|------------|------|-------------|-------------------------|
| `collection1` | Master Data | Description of collection1 | ~100 |
| `collection2` | Time-Series | Description of collection2 | ~10,000 |
| `collection3` | Events | Description of collection3 | ~1,000 |

---

## Collection: `collection1`

**Purpose**: [Describe the purpose of this collection]

**Indexes**:
- `{ field1: 1 }` - Unique index on field1
- `{ field2: 1, field3: -1 }` - Compound index for queries

**Schema**:

| Field | Type | Required | Description | Example | Constraints |
|-------|------|----------|-------------|---------|-------------|
| `_id` | ObjectId | Yes (auto) | MongoDB document ID | `ObjectId("...")` | Auto-generated |
| `code` | String | Yes | Unique identifier code | `"ITEM_001"` | Pattern: `^[A-Z0-9_]+$` |
| `name` | String | Yes | Human-readable name | `"Example Item"` | Max length: 100 |
| `category` | String | Yes | Item category | `"category_a"` | Enum: `["category_a", "category_b", "category_c"]` |
| `status` | String | Yes | Current status | `"active"` | Enum: `["active", "inactive", "pending"]` |
| `metadata` | Object | No | Additional metadata | See below | |
| `metadata.version` | String | No | Version number | `"1.0"` | |
| `metadata.tags` | Array[String] | No | Associated tags | `["tag1", "tag2"]` | |
| `createdAt` | Date | Yes | Creation timestamp (UTC) | `ISODate("2024-01-01T00:00:00Z")` | |
| `updatedAt` | Date | Yes | Last update timestamp (UTC) | `ISODate("2024-01-01T00:00:00Z")` | |

**Example Document**:
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "code": "ITEM_001",
  "name": "Example Item",
  "category": "category_a",
  "status": "active",
  "metadata": {
    "version": "1.0",
    "tags": ["important", "reviewed"]
  },
  "createdAt": ISODate("2024-01-01T00:00:00Z"),
  "updatedAt": ISODate("2024-01-15T10:30:00Z")
}
```

---

## Collection: `collection2` (Time-Series)

**Purpose**: [Describe the purpose of this time-series collection]

**Time-Series Configuration**:
```javascript
{
  timeseries: {
    timeField: "ts",
    metaField: "meta",
    granularity: "seconds"
  }
}
```

**Indexes**:
- Automatic indexes on `meta` and `ts` fields

**Schema**:

| Field | Type | Required | Description | Example | Constraints |
|-------|------|----------|-------------|---------|-------------|
| `ts` | Date | Yes | Timestamp (UTC) | `ISODate("2024-01-01T12:00:00Z")` | Time-series field |
| `meta` | Object | Yes | Metadata (partitioning key) | See below | |
| `meta.sensorId` | String | Yes | Sensor identifier | `"SENSOR_001"` | |
| `meta.location` | String | No | Sensor location | `"Building A"` | |
| `value` | Number | Yes | Measured value | `23.5` | |
| `unit` | String | Yes | Unit of measurement | `"celsius"` | |
| `quality` | String | No | Data quality indicator | `"good"` | Enum: `["good", "fair", "poor"]` |

**Example Document**:
```json
{
  "ts": ISODate("2024-01-01T12:00:00Z"),
  "meta": {
    "sensorId": "SENSOR_001",
    "location": "Building A"
  },
  "value": 23.5,
  "unit": "celsius",
  "quality": "good"
}
```

---

## Collection: `collection3` (Events)

**Purpose**: [Describe the purpose of this events collection]

**Indexes**:
- `{ eventType: 1, timestamp: -1 }` - For filtering by type and time
- `{ status: 1 }` - For finding active events

**Schema**:

| Field | Type | Required | Description | Example | Constraints |
|-------|------|----------|-------------|---------|-------------|
| `_id` | ObjectId | Yes (auto) | Event ID | `ObjectId("...")` | Auto-generated |
| `eventType` | String | Yes | Type of event | `"alert"` | Enum: [list types] |
| `severity` | String | Yes | Event severity | `"high"` | Enum: `["low", "medium", "high", "critical"]` |
| `status` | String | Yes | Current status | `"open"` | Enum: `["open", "acknowledged", "resolved"]` |
| `timestamp` | Date | Yes | When event occurred (UTC) | `ISODate("2024-01-01T12:00:00Z")` | |
| `resolvedAt` | Date | No | When resolved (UTC) | `ISODate("2024-01-01T13:00:00Z")` | |
| `details` | Object | No | Event-specific details | Varies by event type | |

**Example Document**:
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "eventType": "alert",
  "severity": "high",
  "status": "open",
  "timestamp": ISODate("2024-01-01T12:00:00Z"),
  "resolvedAt": null,
  "details": {
    "message": "Temperature exceeded threshold",
    "threshold": 30,
    "actualValue": 32.5
  }
}
```

---

## Relationships Between Collections

### Entity Relationship Diagram (Text)

```
collection1 (1) -----> (N) collection2
     |                         |
     |                         v
     +-----------------> collection3
```

### Foreign Key References

| From Collection | Field | To Collection | Field | Relationship |
|-----------------|-------|---------------|-------|--------------|
| `collection2` | `meta.sensorId` | `collection1` | `code` | Many-to-One |
| `collection3` | `relatedId` | `collection1` | `_id` | Many-to-One |

---

## Data Patterns and Best Practices

### Naming Conventions
- **Collections**: Use camelCase (e.g., `samplingPolicies`)
- **Fields**: Use camelCase (e.g., `createdAt`)
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `ALERT_TYPE_CRITICAL`)

### Timestamps
- Always store in UTC using `Date` type
- Use `ts` for time-series data
- Use `createdAt`/`updatedAt` for audit fields

### Units in Field Names
Include units in field names for clarity:
- `temperatureC` (Celsius)
- `distanceM` (meters)
- `durationMs` (milliseconds)

### Enumerations
Document all possible values for enum fields to ensure consistency.

### Indexes
Create indexes based on:
1. Query patterns (most common filters)
2. Uniqueness constraints
3. Sort requirements

---

## Sample Queries

### Find Recent Events
```javascript
db.collection3.find({
  timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) },
  status: "open"
}).sort({ timestamp: -1 })
```

### Aggregate Time-Series Data
```javascript
db.collection2.aggregate([
  { $match: { ts: { $gte: ISODate("2024-01-01T00:00:00Z") }}},
  { $group: {
    _id: { $dateTrunc: { date: "$ts", unit: "hour" }},
    avgValue: { $avg: "$value" },
    count: { $sum: 1 }
  }}
])
```

---

## Notes

- [Any special considerations for this database]
- [Performance notes or limitations]
- [Future extensions or modifications planned]

---

**Last Updated**: {{CURRENT_DATE}}
**Author**: {{YOUR_NAME}}