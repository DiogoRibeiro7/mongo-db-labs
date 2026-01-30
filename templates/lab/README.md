# Lab Template Usage Guide

This template provides the skeleton structure for creating new MongoDB teaching labs.

## Quick Start

1. **Copy this template to create your new lab:**
   ```bash
   cp -r templates/lab labs/YOUR_LAB_SLUG
   ```

2. **Replace all placeholders:**
   - `{{LAB_NAME}}` - Human-readable lab name (e.g., "IoT Flood Monitoring")
   - `{{LAB_SLUG}}` - Directory name (e.g., "iot_flood_demo")
   - `{{DATABASE_NAME}}` - MongoDB database name (usually same as slug)
   - `{{DOMAIN}}` - Problem domain (e.g., "Environmental Monitoring", "E-commerce")
   - `{{DESCRIPTION}}` - Brief lab description
   - `{{COLLECTIONS}}` - List of collections used
   - `{{YOUR_NAME}}` - Your name for attribution

3. **Customize each file according to your lab requirements**

4. **Test the complete sequence:**
   ```bash
   mongosh 00_setup_mongodb.js
   python 01_seed_project.py
   python 02_simulate_project.py  # if applicable
   mongosh 03_queries_exam.js
   ```

## Template Files

| File | Customization Required |
|------|----------------------|
| `00_setup_mongodb.js` | Define collections, indexes, validators |
| `01_seed_project.py` | Add master/reference data |
| `02_simulate_project.py` | Create time-series generator (optional) |
| `03_queries_exam.js` | Write query exercises |
| `DATABASE.md` | Document every field |
| `README.md` | Explain lab objectives |
| `docker-compose.yml` | Usually no changes needed |
| `requirements.txt` | Add Python dependencies |

## Checklist

Before publishing your lab:

- [ ] All placeholders replaced
- [ ] Scripts run without errors
- [ ] Data model is well-documented
- [ ] Query exercises have solutions
- [ ] README has clear instructions
- [ ] Code has helpful comments
- [ ] Tested with fresh database
- [ ] Added to main README lab table

---

# {{LAB_NAME}}

{{DESCRIPTION}}

## Learning Objectives

- Objective 1
- Objective 2
- Objective 3

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended)
- Python 3.10+
- Basic understanding of [relevant concepts]

## Quick Start

```bash
# Setup database
mongosh 00_setup_mongodb.js

# Install dependencies
pip install -r requirements.txt

# Seed master data
python 01_seed_project.py

# Generate time-series (optional, X hours)
python 02_simulate_project.py --hours X

# Run queries
mongosh 03_queries_exam.js
```

## Database Schema

This lab uses the following collections:
- `collection1` - Description
- `collection2` - Description

See [DATABASE.md](DATABASE.md) for complete schema documentation.

## Lab Exercises

The query file includes exercises covering:
1. Basic aggregations
2. Time-series analysis
3. [Other topics]

## Notes

- [Any special considerations]
- [Performance notes]
- [Extension ideas]