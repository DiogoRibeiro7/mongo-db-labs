# MongoDB Teaching Labs Repository

A comprehensive collection of **MongoDB teaching labs** designed for educational purposes. Each lab provides hands-on experience with NoSQL database concepts, including schema design, time-series analytics, aggregation pipelines, and real-world data modeling scenarios.

## 🎯 Purpose

This repository serves as a teaching resource for:
- **Students** learning MongoDB fundamentals and advanced features
- **Instructors** teaching NoSQL databases with ready-to-use, realistic datasets
- **Developers** practicing MongoDB patterns with production-like scenarios

## 📚 Available Labs

| Lab Name | Slug | Difficulty | Key Topics | Collections | Domain |
|----------|------|------------|------------|-------------|--------|
| **Cold Chain Monitoring System** | `cold-chain-monitoring-mongodb` | Intermediate | Cold chain logistics, Temperature monitoring, Time-series data, ... | 6 (assets, sensors, measurements, ...) | Logistics & Supply Chain |
| **Smart Grid Energy Monitoring System** | `energy-monitoring-smart-grid` | Intermediate | Smart grid infrastructure, Energy consumption patterns, Time-of-use tariffs, ... | 6 (buildings, meters, tariffs, ...) | Energy & Utilities |
| **IoT Flood Risk Monitoring** | `iot_flood_demo` | Intermediate | Time-series data, GeoJSON, Adaptive sampling, ... | 7 (sites, sensors, measurements, ...) | Environmental Monitoring |
| **Smart Parking Occupancy System** | `smart-parking-occupancy` | Intermediate | Smart city infrastructure, Parking management, LoRa/magnetometer sensors, ... | 6 (zones, parking_spots, sensors, ...) | Smart City & IoT |
| **Soil Humidity LoRaWAN Monitoring** | `soil_humidity_lorawan` | Intermediate | Agricultural IoT, LoRaWAN protocol, Soil moisture monitoring, ... | 7 (farms, fields, sensors, ...) | Agriculture IoT |

## 🏗️ Repository Structure

```
mongo-db-labs/
├── README.md                   # This file
├── LICENSE                     # Repository license
├── .gitignore                  # Git ignore rules
│
├── docs/                       # Repository-wide documentation
│   ├── STRUCTURE.md           # Detailed structure guide
│   └── CONTRIBUTING.md        # Contribution guidelines
│
├── scripts/                    # Helper scripts
│   ├── new-lab.py             # Create new lab from template
│   ├── run-lab.py             # Execute lab sequence
│   └── reset-db.py            # Database cleanup utility
│
├── templates/                  # Lab templates
│   └── lab/                   # Standard lab template
│       ├── 00_setup_mongodb.js
│       ├── 01_seed_project.py
│       ├── 02_simulate_project.py
│       ├── 03_queries_exam.js
│       ├── DATABASE.md
│       ├── README.md
│       ├── docker-compose.yml
│       └── requirements.txt
│
└── labs/                       # All teaching labs
    ├── iot_flood_demo/        # IoT flood monitoring lab
    │   ├── __init__.py
    │   ├── 00_setup_mongodb.js
    │   ├── 01_seed_flood_project.py
    │   ├── 02_simulate_flood_project.py
    │   ├── 03_queries_exam.js
    │   ├── DATABASE.md
    │   ├── README.md
    │   ├── docker-compose.yml
    │   └── requirements.txt
    │
    └── soil_humidity_lorawan/ # Soil monitoring lab
        └── ... (same structure)
```

## 📋 Common Lab Layout

Each lab follows a standardized 4-stage execution flow:

### Stage 0: Setup (`00_setup_mongodb.js`)
- Creates database and collections
- Configures time-series collections
- Creates indexes for performance
- Applies JSON schema validators (optional)

### Stage 1: Seed (`01_seed_*.py`)
- Inserts master/configuration data
- Creates sites, sensors, policies
- Sets up reference data (e.g., rating curves)
- Uses deterministic seeding for reproducibility

### Stage 2: Simulate (`02_simulate_*.py`) *[Optional]*
- Generates synthetic time-series data
- Creates realistic telemetry patterns
- Triggers events and alerts
- Accepts parameters: `--hours`, `--seed`, `--base-step-sec`

### Stage 3: Query (`03_queries_exam.js`)
- Exam-style aggregation exercises
- Reference implementations
- Performance analysis queries
- Real-world scenario problems

## 🚀 Getting Started

### Prerequisites

- **Docker** + Docker Compose (Recommended) - Provides consistent MongoDB 7.0
- **mongosh** (MongoDB Shell) - For running queries
- **Python** 3.10+ - For seed/simulation scripts
- **PyMongo** - Install with: `pip install pymongo`

Alternative:
- **MongoDB** 6.0+ (if not using Docker)

### Quick Start with Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mongo-db-labs.git
   cd mongo-db-labs
   ```

2. **Start MongoDB with Docker:**
   ```bash
   # Start shared MongoDB instance (from root directory)
   docker-compose up -d

   # Wait for MongoDB to be ready
   python scripts/wait_for_mongo.py --docker

   # Optional: Enable MongoDB Express GUI
   docker-compose --profile with-gui up -d
   # Access at http://localhost:8081 (admin/admin123)
   ```

3. **Run a complete lab:**
   ```bash
   # Using lab runner (recommended)
   python scripts/lab.py all iot_flood_demo

   # Or run specific stages
   python scripts/lab.py setup iot_flood_demo
   python scripts/lab.py seed iot_flood_demo
   python scripts/lab.py simulate iot_flood_demo --hours 24
   python scripts/lab.py queries iot_flood_demo
   ```

4. **Stop MongoDB when done:**
   ```bash
   docker-compose down
   ```

### Manual Execution (Alternative)

```bash
# Navigate to a lab
cd labs/iot_flood_demo

# With Docker MongoDB running
mongosh mongodb://labuser:labpassword@localhost:27017/ 00_setup_mongodb.js
python 01_seed_flood_project.py
python 02_simulate_flood_project.py --hours 24
mongosh mongodb://labuser:labpassword@localhost:27017/ 03_queries_exam.js
```

### Using Helper Scripts

```bash
# List all available labs
python scripts/lab.py list

# Validate lab structure
python scripts/lab.py validate iot_flood_demo

# Clean lab database
python scripts/lab.py clean iot_flood_demo

# Create a new lab from template
python scripts/new-lab.py my-new-lab
```

## 🐳 Docker Architecture

The repository uses a **unified Docker approach** with a single MongoDB instance shared across all labs:

```yaml
# Root docker-compose.yml provides:
- MongoDB 7.0 with authentication
- Persistent named volumes
- Health checks
- Optional MongoDB Express GUI
- Automatic database initialization
```

**Benefits:**
- ✅ No MongoDB installation required
- ✅ Consistent environment across all labs
- ✅ Shared data volumes (no duplication)
- ✅ Single start/stop for all labs
- ✅ Built-in health checks

**Connection Details:**
| Component | Value |
|-----------|-------|
| MongoDB URI | `mongodb://labuser:labpassword@localhost:27017/` |
| Admin URI | `mongodb://admin:adminpassword@localhost:27017/admin` |
| MongoDB Express | http://localhost:8081 (admin/admin123) |

## 📐 Design Conventions

### Database Naming
- **Database names** match the lab slug (e.g., `iot_flood_demo`)
- **Collection names** use camelCase (e.g., `samplingPolicies`)

### Field Naming
- **All fields** use camelCase in English
- **Metrics** include units: `waterLevelM`, `flowRateM3s`, `rainfallRateMmh`
- **Timestamps**: `ts` (time-series), `createdAt`, `updatedAt` (UTC Date objects)

### Schema Validation
- Each lab includes optional JSON schema validators
- Can be disabled by commenting out validator sections in setup
- Helps students understand data constraints

### Reproducibility
- Seed scripts accept `--seed` parameter for deterministic data
- Setup scripts are idempotent (safe to re-run)
- All labs can be reset to initial state

## 🤝 Contributing

To add a new lab:

1. **Copy the template:**
   ```bash
   cp -r templates/lab labs/your-lab-name
   ```

2. **Customize the lab:**
   - Update all placeholder values in template files
   - Document every field in `DATABASE.md`
   - Provide clear learning objectives in `README.md`

3. **Test thoroughly:**
   - Ensure all scripts run without errors
   - Verify query exercises have solutions
   - Test with different time ranges and seeds

4. **Submit a pull request:**
   - Update this README's lab table
   - Include sample output from queries
   - Add any special requirements

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 📖 Documentation

- [Repository Structure Guide](docs/STRUCTURE.md) - Detailed explanation of file organization
- [Lab Template Guide](templates/lab/README.md) - How to use the lab template
- Individual lab documentation in each `labs/*/README.md`

## 📄 License

This repository is provided for educational purposes. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

These labs were designed for teaching MongoDB concepts in academic and professional training contexts. Special thanks to all contributors who have helped create and refine these educational resources.

---

**Questions?** Open an issue or contact the maintainers.

**Found a bug?** Pull requests are welcome!