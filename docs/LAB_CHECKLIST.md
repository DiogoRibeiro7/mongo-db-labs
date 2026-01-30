# MongoDB Teaching Lab Compliance Checklist

Use this checklist to validate that a MongoDB teaching lab meets all requirements and follows repository conventions. Each lab should score 100% on required items before being merged.

## Quick Validation

```bash
# Run automated checks
python scripts/validate-lab.py <lab-name>

# Or manually review using this checklist
```

---

## Core Requirements Checklist

### 📁 File Structure (Required)

**All files must be present and properly named:**

- [ ] Lab directory exists: `labs/<lab-slug>/`
- [ ] `00_setup_mongodb.js` - Database and collection setup
- [ ] `01_seed_*.py` - Master data seeding script
- [ ] `02_simulate_*.py` - Time-series data generation (optional but recommended)
- [ ] `03_queries_exam.js` - Query exercises with solutions
- [ ] `DATABASE.md` - Complete data dictionary
- [ ] `README.md` - Lab documentation with learning objectives
- [ ] `docker-compose.yml` - Docker configuration (optional but recommended)
- [ ] `requirements.txt` - Python dependencies
- [ ] `__init__.py` - Python package marker (can be empty)

**Score: ___/9** (exclude optional items if not applicable)

---

### 🗃️ Collections (Required)

**Minimum 4-6 collections demonstrating different patterns:**

- [ ] At least 4 collections defined
- [ ] Mix of collection types:
  - [ ] Master data collection (e.g., sites, users, products)
  - [ ] Transactional collection (e.g., orders, transactions)
  - [ ] Time-series collection (e.g., measurements, telemetry)
  - [ ] Event/log collection (e.g., alerts, audit logs)
- [ ] Collections follow camelCase naming
- [ ] Clear relationships between collections

**Example Structure:**
```
✓ Master Data: sites, sensors, users
✓ Time-Series: measurements
✓ Events: alerts
✓ Config: samplingPolicies
```

**Score: ___/4**

---

### ✅ Schema Validation (Required)

**$jsonSchema validation must be present for all non-time-series collections:**

In `00_setup_mongodb.js`:
- [ ] Each collection has `$jsonSchema` validator
- [ ] Required fields are specified
- [ ] Field types are defined (bsonType)
- [ ] Enums are defined for status/type fields
- [ ] Validation level set (`moderate` or `strict`)
- [ ] Validation action set (`error` or `warn`)

**Example:**
```javascript
db.runCommand({
  collMod: "sites",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["siteCode", "name", "createdAt"],
      properties: { /* ... */ }
    }
  },
  validationLevel: "moderate"
})
```

**Score: ___/6**

---

### 🔍 Indexes (Required)

**Appropriate indexes for query performance:**

In `00_setup_mongodb.js`:
- [ ] Unique indexes on identifier fields (e.g., `code`, `email`)
- [ ] Compound indexes for common query patterns
- [ ] Index on tenant/scope field if applicable (e.g., `siteId`, `farmId`)
- [ ] Index on timestamp fields for sorting
- [ ] Text index if full-text search is needed
- [ ] Geospatial index if location queries are used

**Minimum Required:**
- [ ] At least one unique index
- [ ] At least one compound index
- [ ] Indexes match query patterns in `03_queries_exam.js`

**Score: ___/3**

---

### 📝 Naming Conventions (Required)

**All names must follow conventions from [CONVENTIONS.md](CONVENTIONS.md):**

Database & Collections:
- [ ] Database name: `snake_case` (e.g., `iot_flood_demo`)
- [ ] Collection names: `camelCase` (e.g., `samplingPolicies`)
- [ ] English only, no abbreviations

Fields:
- [ ] Field names: `camelCase`
- [ ] Boolean fields: `is*` or `has*` prefix
- [ ] Reference fields: `*Id` suffix (e.g., `userId`)
- [ ] Human-readable IDs: `*Code` suffix (e.g., `siteCode`)
- [ ] Arrays: plural names (e.g., `items`, `tags`)
- [ ] Units in metric names (e.g., `distanceKm`, `temperatureC`)

**Score: ___/9**

---

### ⏰ Required Fields (Required)

**Timestamp and tenant fields per [CONVENTIONS.md](CONVENTIONS.md):**

Entity Collections:
- [ ] `createdAt: ISODate(...)` field present
- [ ] `updatedAt: ISODate(...)` field present
- [ ] `deletedAt` field if soft deletes are used

Time-Series Collections:
- [ ] `ts: ISODate(...)` as time field
- [ ] `meta: {}` object for metadata
- [ ] Tenant ID in meta (e.g., `meta.siteId`)

Tenant Fields (when applicable):
- [ ] IoT: `siteId` or `deviceId`
- [ ] E-commerce: `storeId` or `merchantId`
- [ ] Agriculture: `farmId`
- [ ] SaaS: `tenantId` or `organizationId`

**Score: ___/3** (minimum required fields)

---

### 📊 Time-Series Pattern (If Applicable)

**For labs with time-series data:**

- [ ] Uses MongoDB time-series collection:
  ```javascript
  db.createCollection("measurements", {
    timeseries: {
      timeField: "ts",
      metaField: "meta",
      granularity: "seconds"
    }
  })
  ```
- [ ] Time field named `ts` (not `timestamp` or `time`)
- [ ] Metadata in `meta` object
- [ ] Tenant field in metadata
- [ ] Measurements at root level (not in meta)

**Score: ___/5** (skip if no time-series)

---

### 🐍 Script Quality (Required)

**All scripts must be production-ready:**

`01_seed_*.py`:
- [ ] Shebang line: `#!/usr/bin/env python3`
- [ ] Module docstring explaining purpose
- [ ] Command-line arguments: `--host`, `--port`, `--database`, `--clean`, `--seed`
- [ ] Error handling for MongoDB connection
- [ ] Idempotent (can run multiple times safely)
- [ ] Supports `--clean` flag to reset data
- [ ] Supports `--seed` for reproducible data

`02_simulate_*.py` (if present):
- [ ] Command-line arguments: `--hours`, `--seed`, `--host`, `--port`
- [ ] Batch inserts for performance
- [ ] Realistic data patterns
- [ ] Handles time ranges properly

`00_setup_mongodb.js`:
- [ ] Idempotent (safe to re-run)
- [ ] Creates collections if not exist
- [ ] Handles index conflicts gracefully
- [ ] Clear success/error messages

`03_queries_exam.js`:
- [ ] At least 10 different queries
- [ ] Covers aggregation pipelines
- [ ] Includes performance analysis
- [ ] Solutions provided (can be commented)

**Score: ___/15**

---

### 📚 Documentation (Required)

**Complete and helpful documentation:**

`README.md`:
- [ ] Lab title and description
- [ ] Learning objectives (3-5 items)
- [ ] Prerequisites listed
- [ ] Quick start instructions
- [ ] Docker instructions (if applicable)
- [ ] Expected outcomes explained

`DATABASE.md`:
- [ ] All collections documented
- [ ] Every field documented with:
  - [ ] Field name
  - [ ] Data type
  - [ ] Required/optional
  - [ ] Description
  - [ ] Example value
  - [ ] Constraints/validation
- [ ] Relationships explained
- [ ] Example documents provided
- [ ] Index strategy explained

Code Comments:
- [ ] Scripts have docstrings
- [ ] Complex logic explained
- [ ] Query purpose documented

**Score: ___/11**

---

### 🔒 Security & Best Practices (Required)

**No security issues or bad practices:**

- [ ] No hardcoded credentials
- [ ] No sensitive data in examples
- [ ] No production URLs or endpoints
- [ ] Connection strings parameterized
- [ ] Error messages don't leak sensitive info
- [ ] Example data is appropriate (no PII)

**Score: ___/6**

---

### ✨ Educational Value (Required)

**Lab teaches valuable MongoDB concepts:**

- [ ] Demonstrates at least 3 MongoDB features:
  - [ ] Document model design
  - [ ] Indexing strategies
  - [ ] Aggregation framework
  - [ ] Time-series collections
  - [ ] Schema validation
  - [ ] Transactions (if applicable)
  - [ ] Change streams (if applicable)
- [ ] Progressive difficulty in queries
- [ ] Real-world applicable scenario
- [ ] Performance considerations included

**Score: ___/4**

---

## Summary Scoring

### Required Sections
| Section | Score | Required | Status |
|---------|-------|----------|--------|
| File Structure | ___/9 | 9/9 | ⬜ |
| Collections | ___/4 | 4/4 | ⬜ |
| Schema Validation | ___/6 | 6/6 | ⬜ |
| Indexes | ___/3 | 3/3 | ⬜ |
| Naming Conventions | ___/9 | 9/9 | ⬜ |
| Required Fields | ___/3 | 3/3 | ⬜ |
| Script Quality | ___/15 | 15/15 | ⬜ |
| Documentation | ___/11 | 11/11 | ⬜ |
| Security | ___/6 | 6/6 | ⬜ |
| Educational Value | ___/4 | 4/4 | ⬜ |

**Total: ___/70** (Required: 70/70 for approval)

### Optional Sections
| Section | Score | Status |
|---------|-------|--------|
| Time-Series Pattern | ___/5 | ⬜ |
| Docker Support | ✓/✗ | ⬜ |
| Simulation Script | ✓/✗ | ⬜ |

---

## Quick Review Commands

```bash
# Check file structure
ls -la labs/<lab-name>/

# Validate MongoDB scripts syntax
mongosh --nodb --eval "load('labs/<lab-name>/00_setup_mongodb.js')"

# Check Python syntax
python -m py_compile labs/<lab-name>/*.py

# Count collections defined
grep -c "createCollection" labs/<lab-name>/00_setup_mongodb.js

# Check for validation
grep -c "validator" labs/<lab-name>/00_setup_mongodb.js

# Check for indexes
grep -c "createIndex" labs/<lab-name>/00_setup_mongodb.js

# Verify required fields in DATABASE.md
grep -E "createdAt|updatedAt|ts|meta" labs/<lab-name>/DATABASE.md

# Check query count
grep -c "Query [0-9]" labs/<lab-name>/03_queries_exam.js
```

---

## Common Issues to Check

### 🔴 Automatic Failures
- Missing required files
- No schema validation
- No indexes defined
- Hardcoded credentials
- Non-English field names
- Wrong naming convention (snake_case fields, PascalCase collections)

### 🟡 Warnings (Fix Recommended)
- Less than 4 collections
- No time-series collection
- Missing docker-compose.yml
- Incomplete DATABASE.md
- No error handling in scripts
- Less than 10 queries

### 🟢 Best Practices
- Includes simulation script
- Comprehensive error handling
- Performance analysis in queries
- Multiple collection types
- Clear relationships between collections
- Progressive query difficulty

---

## Certification Levels

### 🥉 Bronze (Minimum Pass)
- All required items complete (70/70)
- Basic functionality verified
- Documentation present

### 🥈 Silver (Good)
- All required items complete
- Time-series pattern implemented correctly
- Docker support included
- Simulation script present

### 🥇 Gold (Excellent)
- All required items complete
- All optional items complete
- Exceptional documentation
- Advanced MongoDB features demonstrated
- Performance optimizations explained
- Could be used as a reference lab

---

## Review Process

1. **Self-Review**: Lab author completes this checklist
2. **Automated Validation**: CI/CD runs checks
3. **Peer Review**: Another contributor validates
4. **Approval**: Maintainer gives final approval

### Sign-off

- [ ] **Author**: I confirm this lab meets all requirements
  - Name: ________________
  - Date: ________________

- [ ] **Reviewer**: I have validated this checklist
  - Name: ________________
  - Date: ________________

- [ ] **Approved**: This lab is approved for merge
  - Name: ________________
  - Date: ________________

---

## Notes Section

Use this space for any additional notes, exceptions, or clarifications:

```
________________________________________________
________________________________________________
________________________________________________
________________________________________________
```

---

**Checklist Version**: 1.0
**Last Updated**: January 2024
**Based on**: [CONVENTIONS.md](CONVENTIONS.md) and [STRUCTURE.md](STRUCTURE.md)