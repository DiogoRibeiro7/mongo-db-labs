# MongoDB Schema Validation Guide

This guide explains how schema validation is implemented across all MongoDB teaching labs to ensure data integrity and teach validation concepts.

## Overview

MongoDB schema validation uses JSON Schema to enforce document structure, data types, and business rules at the database level. This prevents invalid data from entering collections and helps students understand data quality concepts.

## Validation Architecture

```
Collection Definition
        │
        ▼
   JSON Schema
        │
        ├── Structure Rules (required fields, properties)
        ├── Type Rules (bsonType specifications)
        ├── Value Rules (min/max, enums, patterns)
        └── Relationship Rules (references, dependencies)
        │
        ▼
   Validation Level
        │
        ├── strict: All documents
        ├── moderate: New documents only
        └── off: No validation
        │
        ▼
   Validation Action
        │
        ├── error: Reject invalid (default)
        └── warn: Log but allow
```

## Standard Validation Patterns

### 1. Required Fields

```javascript
{
  bsonType: "object",
  required: ["fieldA", "fieldB", "fieldC"],
  properties: {
    fieldA: { bsonType: "string" },
    fieldB: { bsonType: "int" },
    fieldC: { bsonType: "date" }
  }
}
```

### 2. Strict Structure (No Extra Fields)

```javascript
{
  bsonType: "object",
  additionalProperties: false,  // Reject unknown fields
  properties: {
    // Only these fields allowed
  }
}
```

### 3. Enum Constraints

```javascript
{
  sensorType: {
    enum: ["water_level", "flow_rate", "rainfall"],
    description: "Must be one of the allowed sensor types"
  }
}
```

### 4. Numeric Ranges

```javascript
{
  waterLevelM: {
    bsonType: "double",
    minimum: 0.0,
    maximum: 100.0,
    description: "Water level in meters (0-100)"
  },
  batteryPct: {
    bsonType: "int",
    minimum: 0,
    maximum: 100
  }
}
```

### 5. String Patterns

```javascript
{
  siteCode: {
    bsonType: "string",
    pattern: "^[A-Z][A-Z0-9]{3,9}$",
    description: "Uppercase alphanumeric, 4-10 characters"
  },
  email: {
    bsonType: "string",
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  }
}
```

### 6. Nested Object Validation

```javascript
{
  location: {
    bsonType: "object",
    additionalProperties: false,
    required: ["type", "coordinates"],
    properties: {
      type: { enum: ["Point"] },
      coordinates: {
        bsonType: "array",
        minItems: 2,
        maxItems: 2,
        items: [
          { bsonType: "double", minimum: -180, maximum: 180 },
          { bsonType: "double", minimum: -90, maximum: 90 }
        ]
      }
    }
  }
}
```

### 7. Array Validation

```javascript
{
  tags: {
    bsonType: "array",
    minItems: 1,
    maxItems: 10,
    uniqueItems: true,
    items: {
      bsonType: "string",
      enum: ["urgent", "maintenance", "routine"]
    }
  }
}
```

### 8. Conditional Validation

```javascript
{
  oneOf: [
    {
      properties: {
        type: { const: "river" },
        flowRateM3s: { bsonType: "double", minimum: 0 }
      },
      required: ["type", "flowRateM3s"]
    },
    {
      properties: {
        type: { const: "rain_gauge" },
        rainfallMmh: { bsonType: "double", minimum: 0 }
      },
      required: ["type", "rainfallMmh"]
    }
  ]
}
```

## Lab Implementation Standards

### Files Structure

Each lab should include:

```
labs/your_lab/
├── 00_setup_mongodb.js         # Standard validation
├── 00_setup_mongodb_strict.js  # Enhanced validation (optional)
├── 04_bad_inserts.js           # Validation test cases
└── README.md                    # Schema validation section
```

### 04_bad_inserts.js Template

```javascript
// Helper function for testing
function tryInvalidInsert(collection, document, description) {
    print(`\n[TEST] ${description}`);
    print(`Collection: ${collection}`);

    try {
        db[collection].insertOne(document);
        print(`❌ UNEXPECTED: Insert succeeded`);
    } catch (error) {
        print(`✅ EXPECTED: Validation error`);
        print(`Error: ${error.message}`);
    }
}

// Test cases (10-20 per lab)
tryInvalidInsert('collection', {
    // Invalid document
}, 'Description of what validation rule this violates');
```

### README.md Section Template

```markdown
## Schema Validation Exercises

This lab includes schema validation for data integrity.

### Running Validation Tests

\```bash
# Apply validation
mongosh 00_setup_mongodb.js

# Test with invalid documents
mongosh 04_bad_inserts.js
\```

### Key Validation Rules

| Collection | Rules | Example Violations |
|------------|-------|-------------------|
| **collection1** | • Rule 1<br>• Rule 2 | Examples |

### Student Exercises

1. **Exercise Name**
   \```javascript
   // Try invalid insert
   db.collection.insertOne({...});
   \```
```

## Common Validation Rules by Domain

### IoT/Sensor Data

- Timestamp required and must be Date type
- Sensor readings within physical limits
- Battery percentage 0-100
- Signal strength (RSSI) negative values
- Device IDs follow format patterns

### Geospatial Data

- Valid GeoJSON structure
- Coordinates within Earth bounds (-180 to 180, -90 to 90)
- Polygon coordinates form closed loop
- Point type for single locations

### Time-Series Data

- Monotonic timestamps
- Meta field consistency
- Value ranges based on metric type
- Quality flags from allowed list

### Agricultural Data

- Crop types from approved list
- Moisture percentage 0-100
- Temperature within growth ranges
- Field areas positive and reasonable
- Planting dates not in future

### Financial/E-commerce

- Prices non-negative
- Quantities positive integers
- Status from workflow states
- Currency codes ISO 4217
- Timestamps for audit trail

## Testing Validation

### 1. Enable Strict Validation

```javascript
db.runCommand({
  collMod: "collectionName",
  validator: { $jsonSchema: schema },
  validationLevel: "strict",
  validationAction: "error"
});
```

### 2. Test Invalid Documents

```javascript
// Should fail with validation error
db.collection.insertOne({
  // Document missing required fields
});

// Check error details
catch (error) {
  printjson(error.errInfo.details);
}
```

### 3. Temporarily Disable for Testing

```javascript
// Disable validation
db.runCommand({
  collMod: "collectionName",
  validationLevel: "off"
});

// Re-enable
db.runCommand({
  collMod: "collectionName",
  validationLevel: "strict"
});
```

## Best Practices

### DO:
✅ Use `additionalProperties: false` for strict schemas
✅ Add descriptions to complex validation rules
✅ Set reasonable min/max ranges for numeric fields
✅ Use enums for fields with limited valid values
✅ Test validation with comprehensive bad insert examples
✅ Document validation rules in README

### DON'T:
❌ Make validation so strict it prevents legitimate data
❌ Use validation for complex business logic (use application layer)
❌ Forget to test edge cases
❌ Apply validation without documenting it
❌ Use regex patterns that are too restrictive

## Troubleshooting

### Common Issues

1. **"Document failed validation"**
   - Check required fields are present
   - Verify data types match schema
   - Look for typos in field names

2. **"Additional properties are not allowed"**
   - Remove unexpected fields
   - Check for typos in field names
   - Verify schema allows the field

3. **"Does not match any of the enum values"**
   - Check spelling and case
   - Verify value is in allowed list
   - Consider if enum is too restrictive

4. **Performance Impact**
   - Complex schemas can slow inserts
   - Consider using `moderate` level for bulk loads
   - Index fields used in validation

## Teaching Points

When teaching schema validation, emphasize:

1. **Data Quality**: Validation prevents garbage data
2. **Early Detection**: Catch errors at insert time
3. **Documentation**: Schema serves as documentation
4. **Type Safety**: Enforce correct data types
5. **Business Rules**: Encode domain constraints
6. **Consistency**: Ensure uniform data structure

## Resources

- [MongoDB Schema Validation Documentation](https://docs.mongodb.com/manual/core/schema-validation/)
- [JSON Schema Specification](https://json-schema.org/)
- [MongoDB University - Schema Design Patterns](https://university.mongodb.com/)

## Summary

Schema validation is a powerful MongoDB feature that:
- Enforces data integrity at the database level
- Provides clear error messages for invalid data
- Documents expected document structure
- Teaches students about data quality
- Prevents common data entry errors

Each lab should include validation examples that demonstrate these concepts while being relevant to the domain being taught.