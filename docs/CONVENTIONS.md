# MongoDB Teaching Labs - Shared Conventions

This document defines the shared conventions that **ALL** MongoDB teaching labs must follow. These conventions ensure consistency across labs, making it easier for students to focus on learning MongoDB concepts without being distracted by arbitrary differences in data modeling or naming.

## Table of Contents

1. [Naming Conventions](#naming-conventions)
2. [Required Fields](#required-fields)
3. [Time-Series Collections](#time-series-collections)
4. [Schema Validation](#schema-validation)
5. [Indexing Strategy](#indexing-strategy)
6. [Data Types](#data-types)
7. [Relationships and References](#relationships-and-references)
8. [Error Handling](#error-handling)

---

## 1. Naming Conventions

### Database Names
- **Format**: `snake_case`
- **Language**: English only
- **Examples**: `iot_flood_demo`, `ecommerce_orders`, `soil_humidity_lorawan`
- **Rule**: Database name must match the lab directory name

### Collection Names
- **Format**: `camelCase` (plural for entity collections)
- **Language**: English only
- **Examples**:
  - Entity collections (plural): `users`, `products`, `orders`, `sites`, `sensors`
  - Time-series: `measurements`, `events`, `telemetry`
  - Configuration (singular): `config`, `metadata`
  - Lookup tables: `ratingCurves`, `pricingRules`

### Field Names
- **Format**: `camelCase`
- **Language**: English only
- **Prefixes**:
  - Boolean fields: `is*` or `has*` (e.g., `isActive`, `hasExpired`)
  - Arrays: plural forms (e.g., `tags`, `items`, `measurements`)
  - References: `*Id` suffix (e.g., `userId`, `siteId`, `orderId`)
  - Codes: `*Code` suffix for human-readable IDs (e.g., `siteCode`, `productCode`)

### Examples
```javascript
// CORRECT
{
  userId: ObjectId("..."),
  userName: "John Doe",
  isActive: true,
  hasVerifiedEmail: false,
  orderItems: [],
  createdAt: ISODate("2024-01-01T00:00:00Z")
}

// INCORRECT
{
  user_id: "...",          // Wrong: snake_case
  UserName: "John Doe",    // Wrong: PascalCase
  active: true,            // Wrong: missing is/has prefix for boolean
  email_verified: false,   // Wrong: snake_case
  OrderItems: [],          // Wrong: PascalCase
  created_at: "2024-01-01" // Wrong: snake_case and string date
}
```

---

## 2. Required Fields

### Timestamp Fields

Every document that represents an entity or event MUST include appropriate timestamp fields:

#### For Entity Collections (Master Data)
```javascript
{
  // ... other fields ...
  createdAt: ISODate("2024-01-01T00:00:00Z"),  // REQUIRED: When created
  updatedAt: ISODate("2024-01-15T10:00:00Z"),  // REQUIRED: Last modification
  deletedAt: null  // OPTIONAL: For soft deletes
}
```

#### For Time-Series Collections
```javascript
{
  ts: ISODate("2024-01-01T12:00:00Z"),  // REQUIRED: Event timestamp
  meta: { /* ... */ },                   // REQUIRED: Metadata for partitioning
  // ... measurements ...
}
```

#### For Event/Log Collections
```javascript
{
  timestamp: ISODate("2024-01-01T12:00:00Z"),  // REQUIRED: When event occurred
  eventType: "ORDER_PLACED",                    // REQUIRED: Event type
  // ... event data ...
}
```

### Tenant/Scope Fields

When data is scoped to a particular entity (multi-tenant pattern), include appropriate reference fields:

#### Common Tenant Fields by Domain

| Domain | Required Tenant Field | Type | Example |
|--------|----------------------|------|---------|
| IoT/Sensors | `siteId` | ObjectId | Reference to sites collection |
| E-commerce | `merchantId` or `storeId` | ObjectId | Reference to merchants/stores |
| Agriculture | `farmId` | ObjectId | Reference to farms collection |
| SaaS Applications | `tenantId` or `organizationId` | ObjectId | Reference to tenants |
| Education | `schoolId` or `courseId` | ObjectId | Reference to schools/courses |

#### Example: IoT Domain
```javascript
// measurements collection (time-series)
{
  ts: ISODate("2024-01-01T12:00:00Z"),
  meta: {
    siteId: ObjectId("..."),      // REQUIRED: Which site
    sensorId: ObjectId("..."),    // REQUIRED: Which sensor
    metric: "waterLevelM"          // REQUIRED: What metric
  },
  value: 2.45,
  quality: "good"
}
```

#### Example: E-commerce Domain
```javascript
// orders collection
{
  _id: ObjectId("..."),
  storeId: ObjectId("..."),       // REQUIRED: Which store
  customerId: ObjectId("..."),    // REQUIRED: Which customer
  orderNumber: "ORD-2024-0001",
  items: [...],
  createdAt: ISODate("..."),
  updatedAt: ISODate("...")
}
```

---

## 3. Time-Series Collections

### Preferred Pattern: Measurements with Meta Field

All time-series collections MUST follow MongoDB's time-series collection pattern:

```javascript
// Collection creation
db.createCollection("measurements", {
  timeseries: {
    timeField: "ts",           // ALWAYS use "ts" for timestamp
    metaField: "meta",         // ALWAYS use "meta" for metadata
    granularity: "seconds"     // Choose: seconds, minutes, hours
  }
})
```

### Document Structure
```javascript
{
  ts: ISODate("2024-01-01T12:00:00Z"),  // REQUIRED: timestamp
  meta: {                                // REQUIRED: metadata object
    // Tenant/scope identifiers
    siteId: ObjectId("..."),
    sensorId: ObjectId("..."),

    // Categorical data for partitioning
    sensorType: "temperature",
    location: "building-a",

    // Metric identification
    metric: "temperatureC",
    unit: "celsius"
  },
  // Measurements (outside meta)
  value: 23.5,                          // Primary measurement
  quality: "good",                      // Data quality indicator

  // Optional additional measurements
  batteryPct: 85,
  signalStrength: -45
}
```

### Rules for Time-Series Collections

1. **Time Field**: Always use `ts` (not `timestamp`, `time`, or `date`)
2. **Meta Field**: Always use `meta` object for partitioning data
3. **Tenant ID**: Include tenant field in `meta` (e.g., `meta.siteId`)
4. **Metric Type**: Include metric identifier in `meta`
5. **Values**: Keep measurement values at root level (not in meta)

---

## 4. Schema Validation

### Requirement: All Collections Must Have Validation

Every collection (except time-series) MUST have `$jsonSchema` validation:

```javascript
// In 00_setup_mongodb.js
db.runCommand({
  collMod: "sites",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["siteCode", "name", "siteType", "createdAt", "updatedAt"],
      properties: {
        siteCode: {
          bsonType: "string",
          pattern: "^[A-Z0-9_]+$",
          description: "Unique site identifier"
        },
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 100
        },
        siteType: {
          enum: ["river", "stormwater", "rain_gauge"],
          description: "Type of monitoring site"
        },
        createdAt: {
          bsonType: "date"
        },
        updatedAt: {
          bsonType: "date"
        }
      }
    }
  },
  validationLevel: "moderate",  // moderate or strict
  validationAction: "error"     // error or warn
})
```

### Validation Requirements by Field Type

| Field Type | Validation Rules |
|------------|-----------------|
| IDs | `bsonType: "objectId"` |
| Codes | `pattern: "^[A-Z0-9_-]+$"` |
| Names | `minLength: 1, maxLength: 100` |
| Emails | `pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"` |
| Enums | `enum: [...]` with all possible values |
| Dates | `bsonType: "date"` |
| Numbers | `bsonType: "number", minimum: 0` |
| URLs | `pattern: "^https?://"` |

---

## 5. Indexing Strategy

### Required Indexes

Every collection MUST have appropriate indexes:

#### Entity Collections
```javascript
// Unique identifier
db.collection.createIndex({ code: 1 }, { unique: true })

// Tenant field (if applicable)
db.collection.createIndex({ farmId: 1 })

// Common query patterns
db.collection.createIndex({ createdAt: -1 })
db.collection.createIndex({ farmId: 1, createdAt: -1 })
```

#### Time-Series Collections
MongoDB automatically creates indexes on `meta` and `ts` fields.

Additional indexes if needed:
```javascript
// For specific meta field queries
db.measurements.createIndex({ "meta.sensorId": 1, ts: -1 })
```

#### Event Collections
```javascript
// Event type and time
db.events.createIndex({ eventType: 1, timestamp: -1 })

// Status for open events
db.events.createIndex({ status: 1, timestamp: -1 })

// Tenant scoping
db.events.createIndex({ siteId: 1, timestamp: -1 })
```

---

## 6. Data Types

### Strict Type Requirements

| Data Type | MongoDB Type | When to Use | Example |
|-----------|--------------|-------------|---------|
| IDs | ObjectId | All document IDs and references | `ObjectId("...")` |
| Timestamps | Date (ISODate) | ALL date/time fields | `ISODate("2024-01-01T00:00:00Z")` |
| Money | Decimal128 | Financial amounts | `Decimal128("19.99")` |
| Percentages | Number | Store as 0-100, not 0-1 | `85` (meaning 85%) |
| Coordinates | Array[Number] | GeoJSON coordinates | `[lng, lat]` |
| Status/State | String | Use consistent enums | `"ACTIVE"`, `"PENDING"` |

### Units in Field Names

Always include units in field names for clarity:

```javascript
{
  // CORRECT - Units included
  distanceKm: 5.2,
  temperatureC: 23.5,
  durationMs: 1500,
  speedKmh: 60,
  volumeL: 250,
  weightKg: 75,

  // INCORRECT - No units
  distance: 5.2,      // What unit?
  temperature: 23.5,  // Celsius or Fahrenheit?
  duration: 1500,     // Seconds? Milliseconds?
}
```

### GeoJSON Format

For geographic data, always use GeoJSON:

```javascript
{
  location: {
    type: "Point",
    coordinates: [longitude, latitude]  // ALWAYS [lng, lat] order
  }
}
```

---

## 7. Relationships and References

### Reference Patterns

#### Direct Reference (Most Common)
```javascript
// Order document
{
  _id: ObjectId("..."),
  customerId: ObjectId("..."),  // Reference to customers collection
  storeId: ObjectId("..."),     // Reference to stores collection
  // ...
}
```

#### Embedded Documents (For 1:1 or 1:Few)
```javascript
// User document with embedded address
{
  _id: ObjectId("..."),
  name: "John Doe",
  address: {  // Embedded, not referenced
    street: "123 Main St",
    city: "Springfield",
    country: "USA"
  }
}
```

#### Array of References (For 1:Many)
```javascript
// Course document
{
  _id: ObjectId("..."),
  name: "MongoDB 101",
  studentIds: [  // Array of references
    ObjectId("..."),
    ObjectId("..."),
    ObjectId("...")
  ]
}
```

### Naming Convention for References

- Single reference: `<entity>Id` (e.g., `userId`, `orderId`)
- Multiple references: `<entity>Ids` (e.g., `tagIds`, `studentIds`)
- Parent reference: `parentId` or specific name (e.g., `categoryId`)

---

## 8. Error Handling

### Status Fields

Use consistent status values across all collections:

#### Standard Status Values
```javascript
// For entities
status: {
  enum: ["ACTIVE", "INACTIVE", "PENDING", "SUSPENDED", "DELETED"]
}

// For processes/workflows
status: {
  enum: ["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"]
}

// For events/alerts
status: {
  enum: ["OPEN", "ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
}
```

### Error Documents

When storing errors, use consistent structure:

```javascript
{
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid input data",
    details: {
      field: "email",
      reason: "Invalid format"
    },
    timestamp: ISODate("..."),
    stackTrace: "..." // Only in development
  }
}
```

---

## Compliance Checklist

Use this checklist to verify a lab follows conventions:

### Naming
- [ ] Database name is snake_case
- [ ] Collection names are camelCase
- [ ] Field names are camelCase
- [ ] All names are in English
- [ ] Boolean fields use is/has prefix
- [ ] Reference fields use *Id suffix

### Required Fields
- [ ] Entity collections have createdAt/updatedAt
- [ ] Time-series collections use ts field
- [ ] Tenant/scope fields present where applicable
- [ ] Meta field used for time-series

### Data Types
- [ ] All dates use ISODate type
- [ ] All IDs use ObjectId type
- [ ] Units included in field names
- [ ] GeoJSON format for locations

### Validation & Indexes
- [ ] $jsonSchema validation present
- [ ] Required indexes created
- [ ] Unique constraints where needed

---

## Examples

### Good Example: IoT Lab
```javascript
// Collection: sites
{
  _id: ObjectId("..."),
  siteCode: "RIVER_001",      // Human-readable code
  name: "North River Station",
  siteType: "river",           // Enum value
  location: {                  // GeoJSON
    type: "Point",
    coordinates: [-122.3, 47.6]
  },
  createdAt: ISODate("2024-01-01T00:00:00Z"),
  updatedAt: ISODate("2024-01-01T00:00:00Z")
}

// Collection: measurements (time-series)
{
  ts: ISODate("2024-01-01T12:00:00Z"),
  meta: {
    siteId: ObjectId("..."),
    sensorId: ObjectId("..."),
    metric: "waterLevelM"
  },
  value: 2.45,
  quality: "good"
}
```

### Good Example: E-commerce Lab
```javascript
// Collection: orders
{
  _id: ObjectId("..."),
  orderNumber: "ORD-2024-0001",
  storeId: ObjectId("..."),      // Tenant field
  customerId: ObjectId("..."),   // Reference
  status: "PENDING",              // Standard enum
  totalAmount: Decimal128("99.99"),
  items: [
    {
      productId: ObjectId("..."),
      quantity: 2,
      pricePerUnit: Decimal128("25.00")
    }
  ],
  createdAt: ISODate("2024-01-01T10:00:00Z"),
  updatedAt: ISODate("2024-01-01T10:00:00Z")
}
```

---

## Enforcement

These conventions are enforced through:

1. **Code Review**: All PRs checked against these conventions
2. **CI/CD**: Automated validation in GitHub Actions
3. **Templates**: Lab template includes these patterns
4. **Documentation**: LAB_CHECKLIST.md references these rules

---

**Last Updated**: January 2024
**Version**: 1.0
**Maintainer**: MongoDB Labs Team