# Running MongoDB Teaching Labs

This guide explains how to run MongoDB teaching labs using the unified lab runner CLI tool.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Using the Lab Runner](#using-the-lab-runner)
4. [Environment Configuration](#environment-configuration)
5. [Command Reference](#command-reference)
6. [Troubleshooting](#troubleshooting)
7. [Manual Execution](#manual-execution)

---

## Quick Start

The fastest way to run a complete lab:

```bash
# Run everything for a lab (setup → seed → simulate → queries)
python scripts/lab.py all iot_flood_demo

# With custom MongoDB server
MONGO_URI=mongodb://myserver:27017 python scripts/lab.py all soil_humidity_lorawan

# Clean existing data first and simulate 48 hours
python scripts/lab.py all ecommerce-orders --clean --hours 48
```

---

## Prerequisites

### Required Software

1. **MongoDB 6.0+** (7.0+ recommended)
   - Local installation or Docker container
   - Running on default port 27017 or custom

2. **MongoDB Shell (mongosh)**
   - Download: https://www.mongodb.com/try/download/shell
   - Required for setup and query scripts

3. **Python 3.10+**
   - Required for seed and simulation scripts
   - Check version: `python --version`

4. **PyMongo** (Python MongoDB driver)
   ```bash
   pip install pymongo
   ```

### Optional Software

- **Docker & Docker Compose** - For containerized MongoDB
- **Git** - For cloning the repository

---

## Using the Lab Runner

The `lab.py` script provides a unified interface for managing all labs.

### Basic Usage

```bash
python scripts/lab.py <command> <lab-name> [options]
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list` | Show all available labs | `python scripts/lab.py list` |
| `setup` | Create database and collections | `python scripts/lab.py setup iot_flood_demo` |
| `seed` | Insert master/reference data | `python scripts/lab.py seed iot_flood_demo` |
| `simulate` | Generate time-series data | `python scripts/lab.py simulate iot_flood_demo --hours 24` |
| `queries` | Run query exercises | `python scripts/lab.py queries iot_flood_demo` |
| `all` | Run complete sequence | `python scripts/lab.py all iot_flood_demo` |
| `validate` | Check lab structure | `python scripts/lab.py validate iot_flood_demo` |
| `clean` | Drop lab database | `python scripts/lab.py clean iot_flood_demo` |

### Step-by-Step Execution

If you prefer to run steps individually:

```bash
# 1. List available labs
python scripts/lab.py list

# 2. Set up the database structure
python scripts/lab.py setup soil_humidity_lorawan

# 3. Seed with master data
python scripts/lab.py seed soil_humidity_lorawan

# 4. Generate time-series data (optional)
python scripts/lab.py simulate soil_humidity_lorawan --hours 48

# 5. Run query exercises
python scripts/lab.py queries soil_humidity_lorawan
```

---

## Environment Configuration

### MongoDB Connection

Configure MongoDB connection using environment variables:

```bash
# Default: mongodb://localhost:27017
export MONGO_URI=mongodb://localhost:27017

# Custom MongoDB server
export MONGO_URI=mongodb://username:password@myserver:27017

# MongoDB Atlas
export MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net

# With specific database (overrides lab default)
export MONGO_DB=my_custom_database
```

### Windows PowerShell

```powershell
$env:MONGO_URI = "mongodb://localhost:27017"
$env:MONGO_DB = "my_database"
python scripts/lab.py all iot_flood_demo
```

### Windows Command Prompt

```cmd
set MONGO_URI=mongodb://localhost:27017
set MONGO_DB=my_database
python scripts/lab.py all iot_flood_demo
```

---

## Command Reference

### list - Show Available Labs

```bash
python scripts/lab.py list
```

Output:
```
Available MongoDB Teaching Labs
Found 3 lab(s):

ecommerce-orders
  Database: ecommerce_orders
  Scripts: setup | seed | simulate | queries
  Docs: Complete

iot_flood_demo
  Database: iot_flood_demo
  Scripts: setup | seed | simulate | queries
  Docs: Complete
```

### setup - Initialize Database

```bash
python scripts/lab.py setup <lab-name>
```

Creates:
- Database and collections
- Indexes for performance
- Schema validators
- Time-series collection configuration

### seed - Insert Master Data

```bash
python scripts/lab.py seed <lab-name> [--clean]
```

Options:
- `--clean` - Remove existing data before seeding

Inserts:
- Reference data (sites, sensors, users, products)
- Configuration (policies, rules, thresholds)
- Initial state data

### simulate - Generate Time-Series Data

```bash
python scripts/lab.py simulate <lab-name> [--hours N] [--seed N]
```

Options:
- `--hours N` - Hours of data to generate (default: 24)
- `--seed N` - Random seed for reproducible data

Generates:
- Sensor measurements
- Transaction logs
- Event streams
- Alert conditions

### queries - Run Query Exercises

```bash
python scripts/lab.py queries <lab-name>
```

Executes:
- Aggregation pipelines
- Time-series analysis
- Performance benchmarks
- Educational queries

### all - Complete Lab Setup

```bash
python scripts/lab.py all <lab-name> [--clean] [--hours N] [--seed N]
```

Runs the complete sequence:
1. Database setup
2. Data seeding
3. Simulation (if available)
4. Query execution

Options:
- `--clean` - Clean existing data first
- `--hours N` - Simulation duration (default: 24)
- `--seed N` - Random seed for reproducibility

### validate - Check Lab Structure

```bash
python scripts/lab.py validate <lab-name>
```

Checks:
- Required files present
- Database configuration
- Script naming conventions
- Documentation completeness

### clean - Drop Database

```bash
python scripts/lab.py clean <lab-name>
```

**Warning**: This will permanently delete all data in the lab's database.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. mongosh: command not found

**Problem**: MongoDB Shell is not installed or not in PATH.

**Solution**:
```bash
# Install mongosh
# Download from: https://www.mongodb.com/try/download/shell

# Or via package manager:
# macOS
brew install mongosh

# Ubuntu/Debian
sudo apt-get install mongodb-mongosh

# Windows
# Download installer from MongoDB website
```

#### 2. Connection refused on port 27017

**Problem**: MongoDB is not running.

**Solution**:
```bash
# Start MongoDB locally
mongod

# Or with Docker
docker run -d -p 27017:27017 mongo:7

# Or with docker-compose (if lab provides it)
cd labs/<lab-name>
docker compose up -d
```

#### 3. ModuleNotFoundError: No module named 'pymongo'

**Problem**: Python MongoDB driver not installed.

**Solution**:
```bash
pip install pymongo

# Or if lab has requirements.txt
cd labs/<lab-name>
pip install -r requirements.txt
```

#### 4. Authentication failed

**Problem**: MongoDB requires authentication.

**Solution**:
```bash
# Include credentials in MONGO_URI
export MONGO_URI=mongodb://username:password@localhost:27017/admin
python scripts/lab.py all <lab-name>
```

#### 5. Script fails with "No such file or directory"

**Problem**: Running from wrong directory.

**Solution**:
```bash
# Always run from repository root
cd /path/to/mongo-db-labs
python scripts/lab.py all <lab-name>
```

#### 6. Timeout errors during simulation

**Problem**: Large dataset generation takes too long.

**Solution**:
```bash
# Reduce simulation time
python scripts/lab.py simulate <lab-name> --hours 1

# Or run simulation separately with more time
python labs/<lab-name>/02_simulate_*.py --hours 24
```

### Debug Mode

For more verbose output, check the actual command output:

```bash
# The lab.py script shows the actual commands being run
# You can copy and run them manually for debugging:

# Example manual execution
mongosh mongodb://localhost:27017 labs/iot_flood_demo/00_setup_mongodb.js
python labs/iot_flood_demo/01_seed_flood_project.py --host localhost --port 27017
```

---

## Manual Execution

If you prefer to run scripts manually without the CLI tool:

### Option 1: Using Shell Scripts

```bash
cd labs/iot_flood_demo

# Setup
mongosh 00_setup_mongodb.js

# Seed
python 01_seed_flood_project.py

# Simulate
python 02_simulate_flood_project.py --hours 24

# Queries
mongosh 03_queries_exam.js
```

### Option 2: Using Docker Compose

```bash
cd labs/iot_flood_demo

# Start MongoDB
docker compose up -d

# Run scripts against containerized MongoDB
mongosh mongodb://localhost:27017 00_setup_mongodb.js
python 01_seed_flood_project.py
python 02_simulate_flood_project.py
mongosh mongodb://localhost:27017 03_queries_exam.js

# Clean up
docker compose down -v
```

### Option 3: Using Make (if Makefile provided)

```bash
cd labs/iot_flood_demo
make setup
make seed
make simulate
make queries
make clean
```

---

## Best Practices

### For Instructors

1. **Pre-run labs** before class to ensure everything works
2. **Use --seed parameter** for consistent demonstrations
3. **Start with small datasets** (--hours 1) for live demos
4. **Have students validate** their setup first

### For Students

1. **Start with `validate`** to check lab structure
2. **Run `all` command** for complete setup
3. **Use `clean` between attempts** if needed
4. **Check prerequisites** before starting
5. **Read lab README** for specific instructions

### For Development

1. **Test with `validate`** after creating new labs
2. **Use consistent database names** (match directory name)
3. **Include `--clean` flag support** in seed scripts
4. **Make scripts idempotent** (safe to re-run)
5. **Document any special requirements** in lab README

---

## Performance Tips

### Large Datasets

For labs with large datasets:

```bash
# Start with small dataset for testing
python scripts/lab.py simulate <lab> --hours 1

# Then generate full dataset
python scripts/lab.py simulate <lab> --hours 168  # 1 week
```

### Batch Operations

The lab runner uses appropriate batch sizes automatically, but you can optimize:

```bash
# Run simulation directly with custom batch size
cd labs/<lab-name>
python 02_simulate_*.py --hours 24 --batch-size 10000
```

### Resource Monitoring

Monitor MongoDB during large operations:

```javascript
// In another terminal
mongosh
use admin
db.currentOp()  // View running operations
db.stats()      // Database statistics
```

---

## Getting Help

### Documentation

- Lab-specific instructions: `labs/<lab-name>/README.md`
- Database schema: `labs/<lab-name>/DATABASE.md`
- Repository conventions: `docs/CONVENTIONS.md`
- Contributing guide: `docs/CONTRIBUTING.md`

### Command Help

```bash
# General help
python scripts/lab.py --help

# Command-specific help
python scripts/lab.py all --help
python scripts/lab.py simulate --help
```

### Support

- Check existing issues on GitHub
- Read lab-specific README files
- Validate lab structure first
- Ensure all prerequisites are installed

---

**Last Updated**: January 2024
**Tool Version**: 1.0
**Compatibility**: MongoDB 6.0+, Python 3.10+