# Lab Metadata Documentation

This document explains the lab metadata system used to automatically generate lab indexes and documentation.

## Overview

Each lab must include a `lab.json` file containing metadata about the lab. This metadata is used to:
- Generate the lab table in README.md
- Create the comprehensive LABS.md catalog
- Enable automatic discovery of labs
- Provide consistent documentation

## Metadata File Location

Place `lab.json` in the root of your lab directory:

```
labs/
└── your_lab_name/
    ├── lab.json          # Lab metadata (required)
    ├── 00_setup_mongodb.js
    ├── 01_seed_*.py
    ├── README.md
    └── DATABASE.md
```

## Metadata Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name for the lab |
| `slug` | string | Directory name (must match folder) |
| `domain` | string | Industry/domain (e.g., "IoT", "E-commerce") |
| `difficulty` | string | One of: `beginner`, `intermediate`, `advanced` |
| `collections` | array | List of MongoDB collections used |
| `database` | string | MongoDB database name |

### Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `key_topics` | array | Main concepts taught (3-6 items) |
| `learning_outcomes` | array | What students will learn |
| `prerequisites` | array | Required knowledge/software |
| `estimated_time` | string | Time to complete (e.g., "2-3 hours") |
| `files` | object | Script filenames for each stage |
| `tags` | array | Searchable tags |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `sensors` | array | For IoT labs: sensor types |
| `features` | object | Boolean flags for features used |
| `version` | string | Lab version (semantic versioning) |
| `author` | string | Lab author(s) |
| `last_updated` | string | Date of last update (YYYY-MM-DD) |

## Example lab.json

```json
{
  "name": "E-commerce Order Processing",
  "slug": "ecommerce_orders",
  "domain": "E-commerce",
  "difficulty": "intermediate",
  "collections": [
    "customers",
    "products",
    "orders",
    "inventory",
    "reviews"
  ],
  "key_topics": [
    "Document modeling",
    "Transactions",
    "Aggregation pipelines",
    "Inventory management",
    "Real-time analytics"
  ],
  "features": {
    "transactions": true,
    "aggregation_pipelines": true,
    "schema_validation": true,
    "change_streams": false,
    "time_series": false
  },
  "learning_outcomes": [
    "Model e-commerce data in MongoDB",
    "Implement ACID transactions for orders",
    "Build analytics dashboards with aggregations",
    "Handle inventory updates atomically"
  ],
  "prerequisites": [
    "MongoDB 6.0+",
    "Basic understanding of e-commerce",
    "Familiarity with transactions"
  ],
  "estimated_time": "3-4 hours",
  "database": "ecommerce_db",
  "tags": [
    "e-commerce",
    "transactions",
    "retail",
    "analytics"
  ],
  "version": "1.0.0",
  "last_updated": "2024-01-30"
}
```

## Features Object

The `features` object uses boolean flags to indicate which MongoDB features are demonstrated:

```json
"features": {
  "time_series": false,        // Time-series collections
  "geospatial": false,         // GeoJSON and spatial queries
  "schema_validation": true,   // JSON Schema validation
  "aggregation_pipelines": true, // Complex aggregations
  "transactions": false,       // Multi-document ACID transactions
  "change_streams": false,     // Real-time change detection
  "text_search": false,        // Full-text search
  "graphs": false             // Graph lookups
}
```

## Generating Indexes

After creating or updating `lab.json`:

```bash
# Generate/update all indexes
python scripts/build_index.py

# Check if indexes are current
python scripts/build_index.py --check

# Generate JSON format
python scripts/build_index.py --format json
```

## CI/CD Integration

The CI pipeline automatically checks that indexes are up-to-date:

1. **Pre-commit hook**: Checks before committing (optional)
   ```bash
   # Enable pre-commit hook
   git config core.hooksPath .githooks
   ```

2. **GitHub Actions**: Validates on every PR
   - Fails if `lab.json` changes without updating indexes
   - Provides clear error messages

## Adding a New Lab

1. **Create lab directory**:
   ```bash
   mkdir labs/my_new_lab
   ```

2. **Copy template metadata**:
   ```bash
   cp templates/lab/lab.json labs/my_new_lab/
   ```

3. **Edit metadata**:
   - Update all fields with lab-specific information
   - Ensure `slug` matches directory name
   - Add relevant tags and topics

4. **Generate indexes**:
   ```bash
   python scripts/build_index.py
   ```

5. **Commit all changes**:
   ```bash
   git add labs/my_new_lab/lab.json
   git add README.md docs/LABS.md .lab_index_hash
   git commit -m "Add my_new_lab with metadata"
   ```

## Validation Rules

The build script validates:
- `slug` should match directory name
- `difficulty` must be: beginner, intermediate, or advanced
- `collections` array should not be empty
- `database` should be specified
- File paths in `files` should exist

## Best Practices

1. **Keep metadata current**: Update `lab.json` when lab changes
2. **Use consistent naming**: Follow naming conventions
3. **Provide good descriptions**: Help users understand the lab
4. **Tag appropriately**: Use relevant, searchable tags
5. **List all collections**: Include every collection used
6. **Specify prerequisites**: Be clear about requirements
7. **Estimate time realistically**: Test with students

## Troubleshooting

### "Lab index is outdated"

Run the build script:
```bash
python scripts/build_index.py
```

### "No labs found with metadata"

Ensure `lab.json` exists and is valid JSON:
```bash
python -m json.tool labs/my_lab/lab.json
```

### CI fails on index check

The lab metadata changed without updating indexes:
1. Run `python scripts/build_index.py` locally
2. Commit the updated README.md and docs/LABS.md
3. Push changes

## Future Enhancements

Potential improvements to the metadata system:

- **Search functionality**: Find labs by tags/topics
- **Difficulty progression**: Suggest learning paths
- **Dependencies**: Specify prerequisite labs
- **External resources**: Links to documentation/videos
- **Sample data sizes**: Document data volumes
- **Performance metrics**: Expected query times
- **Cloud compatibility**: Atlas-specific features