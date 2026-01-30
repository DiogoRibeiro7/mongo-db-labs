# Repository Structure Guide

This document provides a comprehensive overview of the MongoDB Teaching Labs repository structure, conventions, and best practices.

## Directory Layout

```
mongo-db-labs/
│
├── README.md                      # Main repository documentation
├── LICENSE                        # Repository license (MIT, Apache, etc.)
├── .gitignore                     # Git ignore patterns
│
├── docs/                          # Repository-wide documentation
│   ├── STRUCTURE.md              # This file - repository structure guide
│   └── CONTRIBUTING.md           # Guidelines for contributors
│
├── scripts/                       # Utility scripts for lab management
│   ├── new-lab.py                # Create new lab from template
│   ├── run-lab.py                # Execute complete lab sequence
│   └── reset-db.py               # Database cleanup and reset
│
├── templates/                     # Templates for creating new content
│   └── lab/                      # Standard lab template
│       ├── 00_setup_mongodb.js   # Database setup template
│       ├── 01_seed_project.py    # Data seeding template
│       ├── 02_simulate_project.py # Simulation template
│       ├── 03_queries_exam.js    # Query exercises template
│       ├── DATABASE.md           # Data dictionary template
│       ├── README.md             # Lab documentation template
│       ├── docker-compose.yml    # Docker configuration template
│       └── requirements.txt      # Python dependencies template
│
└── labs/                          # All teaching labs (main content)
    ├── <lab-slug-1>/             # Self-contained lab directory
    ├── <lab-slug-2>/             # Another lab
    └── ...                       # Additional labs
```

## Lab Structure

Each lab is a self-contained unit with its own database, scripts, and documentation.

### Standard Lab Files

| File | Purpose | Required | Naming Convention |
|------|---------|----------|-------------------|
| `00_setup_mongodb.js` | Database and collection setup | ✅ Yes | Always starts with `00_setup_` |
| `01_seed_*.py` | Master/configuration data insertion | ✅ Yes | `01_seed_<project>.py` |
| `02_simulate_*.py` | Time-series data generation | ⚪ Optional | `02_simulate_<project>.py` |
| `03_queries_exam.js` | Query exercises and solutions | ✅ Yes | Always `03_queries_exam.js` |
| `DATABASE.md` | Complete data dictionary | ✅ Yes | Always `DATABASE.md` |
| `README.md` | Lab-specific documentation | ✅ Yes | Always `README.md` |
| `docker-compose.yml` | MongoDB container config | ⚪ Optional | Always `docker-compose.yml` |
| `requirements.txt` | Python dependencies | ⚪ Optional | Always `requirements.txt` |
| `__init__.py` | Python package marker | ⚪ Optional | Always `__init__.py` |

### File Numbering System

Files are numbered to indicate execution order:
- **00**: Setup and initialization
- **01**: Data seeding (master/reference data)
- **02**: Simulation (time-series/events)
- **03**: Queries and exercises

This numbering ensures students run scripts in the correct sequence.

## Database Conventions

### Naming Standards

#### Database Names
- Format: `<lab_slug>` (snake_case)
- Examples: `iot_flood_demo`, `soil_humidity_lorawan`
- Must be unique across all labs
- Should be descriptive but concise

#### Collection Names
- Format: `camelCase`
- Examples: `sites`, `sensors`, `measurements`, `samplingPolicies`
- Plural for entity collections: `users`, `products`, `orders`
- Singular for configuration: `config`, `metadata`

#### Field Names
- Format: `camelCase`
- All fields in English
- Boolean fields start with `is` or `has`: `isActive`, `hasExpired`
- Arrays are plural: `tags`, `measurements`, `items`

### Special Fields

#### Timestamps
| Field | Type | Usage | Timezone |
|-------|------|-------|----------|
| `ts` | Date | Time-series timestamp | UTC |
| `createdAt` | Date | Document creation time | UTC |
| `updatedAt` | Date | Last modification time | UTC |
| `deletedAt` | Date | Soft deletion marker | UTC |
| `validFrom` | Date | Validity period start | UTC |
| `validTo` | Date | Validity period end | UTC |

#### Metrics with Units
Always include units in field names:
- `waterLevelM` (meters)
- `flowRateM3s` (cubic meters per second)
- `temperatureC` (Celsius)
- `pressureKPa` (kilopascals)
- `durationMs` (milliseconds)
- `distanceKm` (kilometers)

#### Identifiers
- `_id`: MongoDB ObjectId (automatic)
- `<entity>Id`: Reference to another document (e.g., `siteId`, `userId`)
- `<entity>Code`: Human-readable identifier (e.g., `siteCode: "RIVER_001"`)

### Collection Types

#### 1. Master Data Collections
Static or slowly-changing reference data:
```javascript
// Example: sites collection
{
  _id: ObjectId("..."),
  siteCode: "RIVER_001",
  name: "North River Station",
  siteType: "river",
  geo: { type: "Point", coordinates: [lng, lat] },
  createdAt: ISODate("2024-01-01T00:00:00Z")
}
```

#### 2. Time-Series Collections
High-frequency telemetry data:
```javascript
// MongoDB time-series collection settings
db.createCollection("measurements", {
  timeseries: {
    timeField: "ts",
    metaField: "meta",
    granularity: "seconds"
  }
})
```

#### 3. Event Collections
Append-only event logs:
```javascript
// Example: alerts collection
{
  _id: ObjectId("..."),
  alertType: "FLOOD_WARNING",
  siteId: ObjectId("..."),
  severity: "high",
  status: "OPEN",
  triggeredAt: ISODate("..."),
  resolvedAt: null
}
```

## Code Patterns

### JavaScript (MongoDB Shell)

#### Setup Script Pattern
```javascript
// 00_setup_mongodb.js
conn = new Mongo();
db = conn.getDB("lab_database");

// Helper function for idempotent collection creation
function createCollectionIfNotExists(name, options = {}) {
    const collections = db.getCollectionNames();
    if (!collections.includes(name)) {
        db.createCollection(name, options);
        print(`Created collection: ${name}`);
    } else {
        print(`Collection exists: ${name}`);
    }
}

// Create collections
createCollectionIfNotExists("sites");
createCollectionIfNotExists("measurements", {
    timeseries: {
        timeField: "ts",
        metaField: "meta"
    }
});

// Create indexes
db.sites.createIndex({ siteCode: 1 }, { unique: true });

// Apply validators (optional)
db.runCommand({
    collMod: "sites",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["siteCode", "siteType"],
            properties: {
                siteCode: { bsonType: "string" },
                siteType: { enum: ["river", "stormwater", "rain_gauge"] }
            }
        }
    }
});
```

#### Query Script Pattern
```javascript
// 03_queries_exam.js
conn = new Mongo();
db = conn.getDB("lab_database");

print("\n=== Query 1: Description ===");
const result1 = db.collection.aggregate([
    // Pipeline stages
]);
printjson(result1);

print("\n=== Query 2: Description ===");
// ...
```

### Python Patterns

#### Seed Script Pattern
```python
#!/usr/bin/env python3
# 01_seed_project.py

import argparse
from datetime import datetime, timezone
from typing import List, Dict
import pymongo
from pymongo import MongoClient

def parse_args():
    parser = argparse.ArgumentParser(description="Seed master data")
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", type=int, default=27017, help="MongoDB port")
    parser.add_argument("--database", default="lab_database", help="Database name")
    parser.add_argument("--clean", action="store_true", help="Clean existing data")
    return parser.parse_args()

def seed_sites(db: pymongo.database.Database, clean: bool = False):
    """Seed site master data."""
    if clean:
        db.sites.delete_many({})
        print("Cleaned sites collection")

    sites = [
        {
            "siteCode": "RIVER_001",
            "name": "North River Station",
            "siteType": "river",
            "createdAt": datetime.now(timezone.utc)
        },
        # More sites...
    ]

    result = db.sites.insert_many(sites)
    print(f"Inserted {len(result.inserted_ids)} sites")

def main():
    args = parse_args()
    client = MongoClient(args.host, args.port)
    db = client[args.database]

    seed_sites(db, clean=args.clean)
    # Seed other collections...

    print("Seeding complete!")

if __name__ == "__main__":
    main()
```

#### Simulation Script Pattern
```python
#!/usr/bin/env python3
# 02_simulate_project.py

import argparse
import random
from datetime import datetime, timedelta, timezone
from typing import Generator
import pymongo
from pymongo import MongoClient

def parse_args():
    parser = argparse.ArgumentParser(description="Simulate time-series data")
    parser.add_argument("--hours", type=float, default=24, help="Hours to simulate")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--base-step-sec", type=int, default=60, help="Base time step")
    return parser.parse_args()

def generate_measurements(start_time: datetime, hours: float, step_sec: int) -> Generator:
    """Generate time-series measurements."""
    current = start_time
    end_time = start_time + timedelta(hours=hours)

    while current < end_time:
        yield {
            "ts": current,
            "meta": {
                "siteId": "...",
                "sensorId": "...",
                "metric": "waterLevelM"
            },
            "value": random.uniform(1.0, 5.0)
        }
        current += timedelta(seconds=step_sec)

def main():
    args = parse_args()
    if args.seed:
        random.seed(args.seed)

    # Simulation logic...

if __name__ == "__main__":
    main()
```

## Docker Configuration

### Standard docker-compose.yml
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: mongodb_lab
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: lab_database

volumes:
  mongodb_data:
```

## Testing Guidelines

### Lab Validation Checklist

Before committing a lab, verify:

1. **Setup Script**
   - [ ] Creates all required collections
   - [ ] Indexes are appropriate
   - [ ] Validators work correctly
   - [ ] Script is idempotent

2. **Seed Script**
   - [ ] Handles `--clean` flag properly
   - [ ] Data is deterministic with `--seed`
   - [ ] All references are valid
   - [ ] No orphaned documents

3. **Simulation Script**
   - [ ] Time ranges work correctly
   - [ ] Data patterns are realistic
   - [ ] Performance is acceptable
   - [ ] Memory usage is bounded

4. **Query Exercises**
   - [ ] All queries have solutions
   - [ ] Solutions are optimized
   - [ ] Output is formatted clearly
   - [ ] Educational value is high

5. **Documentation**
   - [ ] DATABASE.md documents all fields
   - [ ] README.md has clear instructions
   - [ ] Comments explain complex logic
   - [ ] Learning objectives are stated

## Best Practices

### Do's
- ✅ Keep labs self-contained
- ✅ Use deterministic seeding
- ✅ Document every field
- ✅ Include realistic data patterns
- ✅ Provide clear error messages
- ✅ Make scripts idempotent
- ✅ Test with different data volumes
- ✅ Include performance considerations

### Don'ts
- ❌ Hard-code connection strings
- ❌ Use production data
- ❌ Include sensitive information
- ❌ Create cross-lab dependencies
- ❌ Ignore error handling
- ❌ Skip validation
- ❌ Use unclear field names
- ❌ Forget timezone handling

## File Size Guidelines

| File Type | Recommended Max Size | Notes |
|-----------|---------------------|--------|
| Setup scripts | < 500 lines | Split if larger |
| Seed scripts | < 500 lines | Use data files for large datasets |
| Simulation scripts | < 1000 lines | Modularize complex logic |
| Query scripts | < 1000 lines | One query per exercise |
| DATABASE.md | < 50 KB | Be comprehensive but concise |
| README.md | < 10 KB | Focus on essentials |

## Version Control

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New lab or feature
- `fix`: Bug fix in lab
- `docs`: Documentation updates
- `refactor`: Code improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

### Branch Naming
- `lab/<lab-slug>` - New lab development
- `fix/<issue-description>` - Bug fixes
- `docs/<topic>` - Documentation updates

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Collection already exists | Make setup scripts idempotent |
| Duplicate key error | Check unique indexes and data |
| Time-series granularity error | Ensure consistent timestamp precision |
| Memory issues with large datasets | Use batch inserts and streaming |
| Connection refused | Check MongoDB is running and ports are correct |
| Validation failures | Review schema validators and data types |

## Future Extensions

Planned improvements for the repository structure:

1. **Automated Testing**
   - GitHub Actions for lab validation
   - Automated query result verification
   - Performance benchmarking

2. **Student Mode**
   - Scripts without solutions
   - Progressive difficulty levels
   - Hint system

3. **Instructor Tools**
   - Grading automation
   - Progress tracking
   - Custom exercise generation

4. **Advanced Labs**
   - Sharding scenarios
   - Replica set configurations
   - Atlas Search integration
   - Change streams
   - Transactions

---

**Last Updated**: January 2024

**Maintainer**: Repository maintainers

**Questions**: Open an issue on GitHub