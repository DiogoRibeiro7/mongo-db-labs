# Soil Humidity LoRaWAN Monitoring Lab

Agricultural soil monitoring system using LoRaWAN sensors for precision farming and irrigation management.

## Learning Objectives

- Design time-series collections for IoT sensor data
- Implement agricultural domain models with MongoDB
- Use geospatial indexes for farm field boundaries
- Create adaptive irrigation strategies based on soil moisture
- Analyze sensor data patterns with aggregation pipelines
- Handle LoRaWAN-specific IoT patterns

## Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series features)
- Python 3.10+
- Basic understanding of IoT concepts and agriculture

## Quick Start

### Local MongoDB

```bash
# 1. Setup database and collections
mongosh 00_setup_mongodb.js

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Seed master data (farms, fields, sensors, crops)
python 01_seed_soil_humidity.py

# 4. Simulate sensor readings (24 hours of data)
python 02_simulate_soil_humidity.py --hours 24

# 5. Run query exercises
mongosh 03_queries_exam.js
```

### Using Docker

```bash
# Start MongoDB container
docker compose up -d

# Run setup and seeding
mongosh mongodb://localhost:27017 00_setup_mongodb.js
python 01_seed_soil_humidity.py
python 02_simulate_soil_humidity.py --hours 24
mongosh mongodb://localhost:27017 03_queries_exam.js

# Stop when done
docker compose down
```

## Database Schema

This lab uses the `soil_humidity_lorawan` database with 7 collections:

- **farms** - Agricultural sites with owner information
- **fields** - Individual crop fields within farms
- **sensors** - LoRaWAN soil monitoring devices
- **measurements** - Time-series sensor readings (moisture, temperature, pH)
- **irrigationEvents** - Scheduled and completed irrigation activities
- **alerts** - Notifications for critical soil conditions
- **cropTypes** - Reference data for different crops

See [DATABASE.md](DATABASE.md) for complete schema documentation.

## Key Features Demonstrated

### 1. Time-Series Data
- Soil moisture measurements at different depths
- Temperature variations throughout the day
- Efficient storage with MongoDB time-series collections

### 2. Geospatial Queries
- Farm and field locations using GeoJSON
- Finding sensors within field boundaries
- Distance calculations for irrigation planning

### 3. Agricultural Analytics
- Soil moisture trends by field and depth
- Irrigation effectiveness analysis
- Crop-specific moisture requirements
- Alert generation for critical conditions

### 4. LoRaWAN IoT Patterns
- Device EUI management
- Battery monitoring
- Signal quality tracking
- Adaptive sampling based on conditions

## Sample Scenarios

The simulation generates realistic agricultural patterns:

- **Daily cycles**: Moisture decreases during day, stabilizes at night
- **Irrigation events**: Scheduled watering increases moisture levels
- **Weather impacts**: Rain events affect all fields in an area
- **Sensor issues**: Battery depletion, signal loss scenarios
- **Alert conditions**: Low moisture warnings, frost alerts

## Query Exercises

The lab includes 15+ queries covering:

1. Current moisture levels by field
2. Fields requiring irrigation
3. Sensor battery status monitoring
4. Daily moisture averages with moving windows
5. Irrigation effectiveness analysis
6. Alert frequency by type and severity
7. Crop-specific moisture compliance
8. Field productivity metrics
9. Sensor reliability statistics
10. Water usage optimization

## Extensions

Possible enhancements for advanced learning:

- Weather data integration
- Predictive irrigation scheduling
- Multi-depth moisture profiling
- Crop yield correlation
- Water conservation metrics
- Cost optimization models

## Notes

- Soil moisture changes gradually (minutes/hours, not seconds)
- LoRaWAN has specific constraints (data rate, battery life)
- Agricultural decisions are based on trends, not single readings
- Different crops have different moisture requirements
- Soil type affects water retention and sensor readings